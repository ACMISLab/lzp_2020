package QLearning;

import com.alibaba.fastjson.JSONObject;
import netscape.javascript.JSObject;

import java.io.*;
import java.util.*;

public class QLearning {

	public double epsilon = 0.5;		// 探索概率
	public double decay = 0.99;	// 探索概率的每轮衰减
	public double minEpsilon = 0.1;	// 最小探索概率
	public double alpha = 0.5;		// 学习因子
	public double gamma = 0.8;		// 折旧因子
	public int MAX_EPISODES = 1000; 	// 过设置最大迭代次数来控制训练轮数
	public int iteration = 4;
	public int targetStep = 10;		// 动作-并发阈值每轮增减值
	public int minConcurrency = 10;
	public int maxConcurrency = 190;
	public int minUtilization = 50;
	public int maxUtilization = 100;
	public int bin = 2; 				// cpu、mem资源利用率bin大小

	AutoscaleController autoscaleController = new AutoscaleController();

	public String QMapPath = "D:\\Seepen\\ACMIS\\MyGraduation\\cold-2\\src\\main\\java\\qlearning_report\\Qmap.txt";

	// Q表。考虑可扩展性，<state, <action, Q-value>>
	public Map<String, Map<String, Double>> QMap = new HashMap<>();


	public static void main(String[] args) throws InterruptedException, IOException, ClassNotFoundException {

		QLearning qLearning = new QLearning();
		for(int i=0;i<10;i++) {
			qLearning.startTrain(i+21);
			Thread.sleep(120000);
		}

 		System.out.println("see Qmap");
	}

	/**
	 *
	 * @param
	 * @return void
	 * @author Seepen
	 * @creed: Talk is cheap,show me the code
	 * @date 2022/11/27 22:16
	 */
	public void startTrain(int round) throws InterruptedException, IOException, ClassNotFoundException {
		int initTarget = 100;
		int initUtil = 70;

		ArrayList<ArrayList<String>> list = new ArrayList<>();		// 写入文件

		int targetAct;				// 当前并发阈值的动作
		int utilizationAct;			// 利用率
		String curAct;				// 当前总的动作

		int curConcur = initTarget;	// 当前并发限制
		int curUtil = initUtil;	// 当前利用率
		int curCPU;				//
		int curMem;
		String curEnv;				// 当前总的环境

		int nextConcur;			// 下一轮并发限制
		int nextCPU;				//
		int nextMem;
		String nextEnv;				// 当前总的环境

		List<Double> systemInfo;
		loadMap();

		// 对每轮训练，一轮是一次配置更新
		for(int episode = 0; episode < MAX_EPISODES; episode++) {
			System.out.println("round "+episode+"...");
			ArrayList<ArrayList<String>> res = new ArrayList<>();		// 交互以后的性能数据，为取平均值，每轮迭代5次，去极值取平均

			// 获取当前环境
			systemInfo = autoscaleController.myPrometheusClient.getSystemInfo(System.currentTimeMillis());
			curCPU = systemInfo.get(0).intValue() / bin;
			curMem = systemInfo.get(1).intValue() / bin;
			curEnv = Arrays.toString(new int[]{curConcur, curCPU, curMem});
			System.out.println("cur env "+curEnv);

			// 更新探索概率因子
//			if(episode>100 && epsilon>minEpsilon){
//				epsilon *= decay;
//			}
			if(epsilon>minEpsilon){
				epsilon *= decay;
			}

			// 概率探索
			if(false || Math.random() < epsilon || !QMap.containsKey(curEnv)){
				targetAct = randomAction();
				utilizationAct = randomAction();
				System.out.print("exploring select ");
			// 不探索，根据Q表选择当前环境状态下，Q值最大的动作
			}else{
//				targetAct = max(curEnv);
				int[] tem = maxAct(curEnv);
				targetAct = tem[0];
				utilizationAct = tem[1];
				System.out.print("recording Q table ");
			}

			curAct = Arrays.toString(new int[]{targetAct, utilizationAct});
			System.out.println("actions is "+curAct);

			// 根据动作进行更新交互，得到当前要执行的配置，收集新的性能数据、环境数据
			curConcur += targetAct*targetStep;
			curConcur = Math.max(minConcurrency, curConcur);
			curConcur = Math.min(maxConcurrency, curConcur);
			curUtil += utilizationAct*targetStep;
			curUtil = Math.max(minUtilization, curUtil);
			curUtil = Math.min(maxUtilization, curUtil);
			// 当两个维度的动作均为0时，不需变动
			if(targetAct==0 && utilizationAct==0) res.add(autoscaleController.executePlanWithoutChange(episode, curConcur, curUtil, round, 1));
			else res.add(autoscaleController.executePlanWithChange(episode, curConcur, curUtil, round, 1));

			for(int i=1;i<iteration;i++) res.add(autoscaleController.executePlanWithoutChange(episode, curConcur, curUtil, round, i+1));

			ArrayList<String> resAvg = getAvgRes(res);


//			curEnv = Arrays.toString(new int[]{curConcur, curCPU, curMem});

			// 更新环境变量
			long startTime = Long.parseLong(resAvg.get(resAvg.size()-2));
			long endTime = Long.parseLong(resAvg.get(resAvg.size()-1));
			systemInfo = autoscaleController.myPrometheusClient.getSystemInfo(startTime);
			nextCPU = systemInfo.get(0).intValue() / bin;
			nextMem = systemInfo.get(1).intValue() / bin;
			nextConcur = curConcur;
			nextEnv = Arrays.toString(new int[]{nextConcur, nextCPU, nextMem});
			System.out.println("next env "+nextEnv);

			// 计算 reward
			double throughput = Double.parseDouble(resAvg.get(2));
			double latencyAvg = Double.parseDouble(resAvg.get(3));
			double latencyP90 = Double.parseDouble(resAvg.get(4));
			double reward = throughput / (0.8*latencyAvg + 0.2*latencyP90) * 100;
			System.out.println("reward is " + reward);


			// 根据计算贝尔曼方程计算Q值
			double QValue;
			// 如果原值存在，用方程更新值
			if(QMap.containsKey(curEnv) && QMap.get(curEnv).containsKey(curAct))
				QValue = (1-alpha)*QMap.get(curEnv).get(curAct) + alpha*(reward+gamma*maxNextQValue(nextEnv));
			// 如果原值不存在，直接不考虑旧值，
			else{
				QValue = reward+gamma*maxNextQValue(nextEnv);
			}

			// 更新Q表
			if(!QMap.containsKey(curEnv)){
				QMap.put(curEnv, new HashMap<>());
			}
			QMap.get(curEnv).put(curAct, QValue);

			// 将此轮结果添加到训练报告中
			resAvg.add(curEnv);
			resAvg.add(curAct);
			resAvg.add(String.valueOf(reward));
			list.add(resAvg);

//			outputMap(QMap);
			autoscaleController.write2Csv("D:\\Seepen\\ACMIS\\MyGraduation\\cold-2\\src\\main\\java\\a-test-qlearning-res-new-"+round+".csv", list);
			storeMap();
//			outputMap(QMap);
		}

		autoscaleController.write2Csv("D:\\Seepen\\ACMIS\\MyGraduation\\cold-2\\src\\main\\java\\a-test-qlearning-res-new-"+round+".csv", list);

	}

	public ArrayList<String> getTrainRes(int episode, int round, int curConcur, int curUtil, int targetAct, int utilizationAct) throws InterruptedException {
		ArrayList<ArrayList<String>> res = new ArrayList<>();		// 交互以后的性能数据，为取平均值，每轮迭代5次，去极值取平均
		if(targetAct==0 && utilizationAct==0) res.add(autoscaleController.executePlanWithoutChange(episode, curConcur, curUtil, round, 1));
		else res.add(autoscaleController.executePlanWithChange(episode, curConcur, curUtil, round, 1));
		for(int i=1;i<iteration;i++) res.add(autoscaleController.executePlanWithoutChange(episode, curConcur, curUtil, round, i+1));
		ArrayList<String> ress = getAvgRes(res);

		return ress;
	}

	/**
	 * 纯随机选取动作
	 * @return
	 */
	public int randomAction(){
		double rand = Math.random();
		if(rand<=0.33)	return 1;
		else if(rand<=0.66) return 0;
		else if(rand<=0.99) return -1;
		else return randomAction();
	}

	/**
	 * 随机给定环境下未解锁动作
	 * @param env
	 * @return
	 */
	public int randomWithNewAction(String env){
		double rand = Math.random();
		int act = 0;
		if(rand<=0.33)	act = 1;
		else if(rand<=0.66) act = 0;
		else if(rand<=0.99) act = -1;
		else return randomWithNewAction(env);

		int[] acts = new int[]{act};
		String curAction = Arrays.toString(acts);
		// 如果选中了已有的动作，就重新选
		if(QMap.get(env).containsKey(curAction)) return randomWithNewAction(env);
		else {
			System.out.println("action is not unlock all, now choose "+env+" : "+act);
			return act;
		}

	}

	public int[] randomWithNewAction2(String env){
		int act1 = randomAction();
		int act2 = randomAction();

		int[] acts = new int[]{act1, act2};
		String curAction = Arrays.toString(acts);
		// 如果选中了已有的动作，就重新选
		if(QMap.get(env).containsKey(curAction)) return randomWithNewAction2(env);
		else {
			System.out.println("action is not unlock all, now choose "+env+" : "+curAction);
			return acts;
		}

	}


	/**
	 * 从当前环境下选出Q值最大的动作，若动作不全则优先随机选未解锁动作
	 * @param env
	 * @return
	 */
	public int max(String env){
		Map<String, Double> actionTable = QMap.get(env);
		String res = "";
		double maxQValue = Double.MIN_VALUE;
		if(actionTable.size()<3){
			return randomWithNewAction(env);
		}
		for(String s : actionTable.keySet()){
			if(actionTable.get(s) > maxQValue){
				maxQValue = actionTable.get(s);
				res = s;
			}
		}
		String[] acts = res.substring(1,res.length()-1).split(", ");
		return Integer.parseInt(acts[0]);

	}

	public int[] maxAct(String env){
		Map<String, Double> actionTable = QMap.get(env);
		String res = "";
		double maxQValue = Double.MIN_VALUE;
		if(actionTable.size()<7){
			return randomWithNewAction2(env);
		}
		for(String s : actionTable.keySet()){
			if(actionTable.get(s) > maxQValue){
				maxQValue = actionTable.get(s);
				res = s;
			}
		}
		String[] acts = res.substring(1,res.length()-1).split(", ");

		return new int[]{Integer.parseInt(acts[0]), Integer.parseInt(acts[1])};
	}


	/**
	 * 计算未来（下一步）可获取的最大Q值，作为此轮动作Q值的一个参考
	 * @param env
	 * @return
	 */
	public double maxNextQValue(String env){
		System.out.println(env);
		if(!QMap.containsKey(env)) return 0;
		else{
			double maxQValue = Double.MIN_VALUE;
			for(double d : QMap.get(env).values()){
				maxQValue = Math.max(maxQValue, d);
			}
			return maxQValue;
		}
	}

	public double max3rows(String env){
		String[] ss = env.substring(1,env.length()-1).split(", ");
		int conc = Integer.parseInt(ss[0]);
		double max = 0;
		for(int i=Math.max(minConcurrency,conc);i<=Math.min(maxConcurrency, conc);i+=10){
			ss[0] = String.valueOf(i);
			max = Math.max(max, maxNextQValue(Arrays.toString(ss)));
		}
		return max;


	}

	public void outputMap(Map<String, Map<String, Double>> map){
		for(String s1 : map.keySet()){
			System.out.print(s1+"  ");
			Map<String, Double> map1 = map.get(s1);
			for(String s2 : map1.keySet()){
				System.out.print(" "+s2+" ");
				System.out.print(map1.get(s2));
			}
			System.out.println();
		}

	}

	public double getAvgValue(ArrayList<ArrayList<String>> list, int index){
		double[] a = new double[list.size()];
		for(int i=0;i<list.size();i++){
			a[i] = Double.parseDouble(list.get(i).get(index));
		}
		Arrays.sort(a);
		System.out.println(Arrays.toString(a));
		double dum = 0;
		for(int i=1;i<a.length-1;i++){
			dum += a[i];
		}
		return dum / (a.length-2);
	}

	public ArrayList<String> getAvgRes(ArrayList<ArrayList<String>> list){
		ArrayList<String> res = new ArrayList<>();
		System.out.println("res list is\n");
		System.out.println(Arrays.toString(list.toArray()));

		res.add(list.get(list.size()-1).get(0));
		res.add(list.get(list.size()-1).get(1));
		res.add(String.valueOf(getAvgValue(list, 2)));
		res.add(String.valueOf((int)getAvgValue(list, 3)));
		res.add(String.valueOf((int)getAvgValue(list, 4)));
		res.add(String.valueOf((int)getAvgValue(list, 5)));
		res.add(String.valueOf((int)getAvgValue(list, 6)));
		res.add(list.get(0).get(7));
		res.add(list.get(list.size()-1).get(8));
		res.add(list.get(list.size()-1).get(9));

		return res;

	}

	public void storeMap() throws IOException {
		FileOutputStream fos = new FileOutputStream("D:\\Seepen\\ACMIS\\MyGraduation\\cold-2\\src\\main\\java\\test-Qmap.txt");
		ObjectOutputStream outputStream = new ObjectOutputStream(fos);
		outputStream.writeObject(QMap);
		outputStream.close();
	}

	public void loadMap() throws IOException, ClassNotFoundException {
		FileInputStream fis = new FileInputStream("D:\\Seepen\\ACMIS\\MyGraduation\\cold-2\\src\\main\\java\\Qmap.txt");
		ObjectInputStream objectInputStream = new ObjectInputStream(fis);
		QMap = (Map<String, Map<String, Double>>) objectInputStream.readObject();
		objectInputStream.close();

	}

	/**
	 * 保存此轮训练为历史数据。
	 * 读取需要 当前环境状态、当前配置、
	 */

}

