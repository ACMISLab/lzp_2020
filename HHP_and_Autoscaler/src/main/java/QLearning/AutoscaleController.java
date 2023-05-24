package QLearning;

import Knative_Entity.MyKnativeClient;
import Jmeter_pkg.JmeterClient;
import Prometheus_Client.MyPrometheusClient;
import io.fabric8.knative.serving.v1.Service;
import org.apache.jmeter.report.config.ConfigurationException;
import org.apache.jmeter.report.dashboard.GenerationException;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

/**
 * 整个自动伸缩实验总控函数
 * 流程：
 	 * 1. 更新revision的并发配置
	 * 2. Knative 集群完成新reviosn创建、route流量重定向
	 * 3. 调用 Jemeter API 发送并发请求
	 * 4. 等待 Jemeter 完成实验，收集性能数据
	 * 5. 调用 prometheus 收集集群资源数据
	 * 6. 使用性能数据与资源数据，在 RL 模型中训练并得到最佳并发配置
	 * 7. 重复 Step 1
	 *
 * @author Seepen
 * @date 2022/11/19 16:03
 */
public class AutoscaleController {

	String reportPath = "D:\\Seepen\\ACMIS\\MyGraduation\\cold-2\\src\\main\\java\\Jmeter_report";

	// 待测Ksvc信息
	String ksvcName = "floating";
	String ksvcNamespace = "default";

	// 压测信息
	String testKsvcUrl = "floating.default.example.com";
	String postBody = "{\"n\":200}";
	int concurrencyNum = 100;
	int rampUp = 1;

	// validationTest 中控制并发配置
	int minTarget = 10;
	int maxTarget = 190;
	int step = 10;

	MyKnativeClient myKnativeClient = new MyKnativeClient();
	JmeterClient jmeterClient = new JmeterClient();
	MyPrometheusClient myPrometheusClient = new MyPrometheusClient();

	/**
	 * 实验一 控制流程
	 * @return void
	 * @author Seepen
	 * @date 2022/11/19 20:26
	 */
	public void firstTestOfValidation(String path) throws InterruptedException {

		ArrayList<ArrayList<String>> list = new ArrayList<>();
		Map<String, String> paramsMap = new HashMap<>();

		// 对每一个并发配置
		for(int target = minTarget; target <= maxTarget; target += step){
//			paramsMap.put("target", String.valueOf(target));
			paramsMap.put("hardLimit", String.valueOf(target));
			paramsMap.put("utilization", "100");
			// 更新revision配置
			Service newKsvc = myKnativeClient.updateKsvc(ksvcNamespace, ksvcName, paramsMap);

//			long time1 = System.currentTimeMillis();
//			System.out.println(res.getStatus().getConditions().get(2).getStatus());
//			while(res.getStatus().getConditions().get(2).getStatus().equals("False")){
//				System.out.println(System.currentTimeMillis() - time1);
//			}

			// 等revision准备好
			System.out.println("target="+target+" revision creating");
			// 等待上一个 revision pod 全部停止 及新revision准备好
			Thread.sleep(20000);

			// 执行压测
			System.out.println("target="+target+" Jmeter Starting");
			ArrayList<String> res = jmeterClient.executePlan(testKsvcUrl, postBody, concurrencyNum, rampUp, target,70, path);
			list.add(res);

		}

		write2Csv(path + "\\a-floating-report_all.csv", list);

	}


	public ArrayList<String> executePlanWithoutChange(int episode, int tar, int u,int round, int iteration) throws InterruptedException {
		Thread.sleep(5000);
		String roundPath = reportPath + "\\round_" + round +"\\episode_"+(episode+1) + "\\iteration_"+iteration+"_";
		return jmeterClient.executePlan(testKsvcUrl, postBody, concurrencyNum, rampUp, tar, u, roundPath);

	}

	public ArrayList<String> executePlanWithChange(int episode, int target, int utilization, int round, int iteration) throws InterruptedException {

		Map<String, String> paramsMap = new HashMap<>();
		String roundPath = reportPath + "\\round_" + round +"\\episode_"+(episode+1) + "\\iteration_"+iteration+"_";

//		paramsMap.put("target", String.valueOf(target));
		paramsMap.put("hardLimit", String.valueOf(target));
		paramsMap.put("utilization", String.valueOf(utilization));
		// 更新revision配置
		myKnativeClient.updateKsvc(ksvcNamespace, ksvcName, paramsMap);

		// 等revision准备好
		System.out.println("target="+target+" utilization="+utilization+" revision creating");
		// 等待上一个 revision pod 全部停止 及新revision准备好
		Thread.sleep(35000);
		// 执行压测
		System.out.println("Jmeter Starting");

		return jmeterClient.executePlan(testKsvcUrl, postBody, concurrencyNum, rampUp, target, utilization, roundPath);

	}

	/**
	 * 将此轮测试结果写入文件
	 * @param csvPath
	 * @param list
	 */
	public void write2Csv(String csvPath, ArrayList<ArrayList<String>> list){

		File writeResult = new File(csvPath);

		try {
			BufferedWriter writer = new BufferedWriter(new FileWriter(writeResult));
			for(int i=0;i<list.size();i++) {
				String curLine = list.get(i).toString();
				curLine = curLine.substring(1,curLine.length()-1);
				System.out.println(curLine);
				writer.write(curLine);
				writer.newLine();
			}

			writer.flush();
			writer.close();

		}catch (Exception e){
			e.printStackTrace();
		}
	}



	public static void main(String[] args) throws InterruptedException, GenerationException, ConfigurationException {

		AutoscaleController autoscaleController = new AutoscaleController();

		for(int i=0;i<5;i++){

			String roundPath = autoscaleController.reportPath + "\\round_" + (i+1);
			autoscaleController.firstTestOfValidation(roundPath);
		}

	}
}
