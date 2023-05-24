package Cold_Start_Strategy;//import cn.hutool.core.date.StopWatch;

import java.io.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

import com.alibaba.fastjson.JSONObject;
import org.apache.http.HttpEntity;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.util.EntityUtils;

public class HybridHistogram {
    static int histogramRange = 240;       // 直方图记录范围，默认四小时
    static int OOBThreshold = 8;           // OOB 次数阈值
    static double COVThreshold = 4;      // CoV 阈值
    static double headPercentageThreshold = 0.05;     // 直方图头部百分位
    static double tailPercentageThreshold = 0.95;    // 直方图尾部百分位
    static Map<Integer, MyFunction> allFuncMap = new HashMap<>();   // 记录每个函数 <id, 函数类>
    static ArrayList<String> HashFunctions = new ArrayList<>();
    static ArrayList<String> HashOwners = new ArrayList<>();
    public static void main(String[] args) {
        HybridHistogram hybridHistogram = new HybridHistogram();
//        String path = "D:\\Seepen\\ACMIS\\毕设相关\\毕设工程工作\\coldStartStrategy\\dataSet\\appData_2019_14_days.csv";
        String path = "D:\\Seepen\\ACMIS\\MyGraduation\\project_work\\coldStartStrategy\\dataSet\\sevenDays\\series_Data_2019_1-7_days.csv";
        Map<Integer, int[][]> data = hybridHistogram.loadData(path);

        hybridHistogram.policyController(data);

        System.out.println("end");
        double[] res = hybridHistogram.coldStartStatistic(allFuncMap);
        System.out.println(Arrays.toString(res));
        System.out.println("endddd");

    }

    /**
     * 加载数据。从csv文件中读取函数ID，返回函数调用map，<id, [[调用时刻序列], [时刻内调用数序列]]>
     * @param
     * @return java.util.Map<java.lang.Integer,int[][]>
     * @author Seepen
     * @creed: Talk is cheap,show me the code
     * @date 2022/8/17 10:39
     */
    Map<Integer, int[][]> loadData(String path) {
        Map<Integer, int[][]> data = new HashMap<>();       // 函数的调用序列
        // 从csv文件，将funcID序列及其调用时刻序列读到数组中
        try {
            BufferedReader reader = new BufferedReader(new FileReader(path));
            String line = null;
            int index = 0;
            while ((line = reader.readLine()) != null) {
                if(index==0){
                    index++;
                    continue;
                }
                String[] item = line.split(";");        //一行数组, 包含函数id、调用时间序列、调用次数序列
//                System.out.println(line);
                // 1. app 相关的文件
//                String[] timeSeries = item[2].substring(1,item[2].length()-1).split(", ");
//                String[] numberSeries = item[3].substring(1,item[3].length()-1).split(", ");
                // 2. func 相关的文件
                String[] timeSeries = item[6].substring(1,item[6].length()-1).split(", ");
                String[] numberSeries = item[7].substring(1,item[7].length()-1).split(", ");
                HashFunctions.add(item[3]);
                HashOwners.add(item[1]);

                int[][] series = new int[2][];
                series[0] = Arrays.stream(timeSeries).mapToInt(Integer::parseInt).toArray();
                series[1] = Arrays.stream(numberSeries).mapToInt(Integer::parseInt).toArray();
                data.put(Integer.valueOf(item[0]), series);
                index++;
            }
        }catch (Exception e){
            e.printStackTrace();
        }

        return data;

    }

    String httpRequest(String api, String data) throws IOException {
        CloseableHttpClient client = HttpClientBuilder.create().build();
        String url = "http://192.168.103.101:10000/"+api;
        HttpPost httpPost = new HttpPost(url);
        httpPost.setHeader("Content-Type", "application/json;charset=UTF-8");
        JSONObject jsonObject = new JSONObject();
        jsonObject.put("data", data);

        StringEntity entity = new StringEntity(jsonObject.toJSONString(), "UTF-8");
        entity.setContentType("application/json");
        httpPost.setEntity(entity);

        CloseableHttpResponse execute = client.execute(httpPost);
        HttpEntity httpEntity = execute.getEntity();
        String s = EntityUtils.toString(httpEntity);
        JSONObject json = JSONObject.parseObject(s);
        client.close();

        String result = json.getString("res");

        return result;

    }

    // 通过python脚本调用模型、存档用
    int usePythonScript(String type, int[] nums){
        // cmd=“你想用的指定python环境的绝对路径”，“.py脚本的绝对路径”，String.valueOf（nums）；
        // 只能传String类型，传不了list，用String.valueOf(list)才可
        String res = "";
        String path = type.equals("ARIMA") ?
                "ARIMA_model.py"
                : "LSTM_model.py";
        String[] cmds = new String[]{
                "C:\\Users\\Seepen\\AppData\\Roaming\\python\\Python36\\python.exe",
                "D:\\Seepen\\ACMIS\\毕设相关\\毕设工程工作\\coldStartStrategy\\models\\"+path,
                Arrays.toString(nums)
        };
        System.out.println("ARIMA used " + Arrays.toString(nums));

        try{
            Process process = Runtime.getRuntime().exec(cmds);

            // 获取
            BufferedReader in = new BufferedReader(new InputStreamReader(process.getInputStream()));
            res = in.readLine();
            res = res.equals("") ? Integer.toString(nums[nums.length-1]) : res.substring(1,res.length()-1); // 防空

//            System.out.println("res is " + res);
        }catch (Exception e){
            e.printStackTrace();
        }

        return (int)Math.round(Double.parseDouble(res));
    }

    /**
     * 调用 python 脚本，将时间序列传入，然后调用预测模型，返回下一次调用时刻的预测值
     * @param type
	 * @param nums
     * @return int
     * @author Seepen
     * @creed: Talk is cheap,show me the code
     * @date 2022/9/18 16:35
     */
    int invokePython(String type, int[] nums) throws IOException {

        String res = "";

        try{
            res = httpRequest(type, Arrays.toString(nums));
            res = res.equals("") ? Integer.toString(nums[nums.length-1]) : res.substring(1,res.length()-1); // 防空

        }catch (Exception e){
            e.printStackTrace();
        }

        return (int)Math.round(Double.parseDouble(res));

    }

    /**
     * 整个优化策略的流程控制器
     * 遍历处理好的数据，对每个函数，遍历其每一次调用，更新直方图并选择不同的组件进行窗口值更新
     * 统计每个函数每次调用是否是冷启动；若是冷启动，记录此时的窗口值
     * @param data
     * @return void
     * @author Seepen
     * @creed: Talk is cheap,show me the code
     * @date 2022/8/18 11:01
     */
    void policyController(Map<Integer, int[][]> data){
        int n = data.size();
//        int n=7000;
//        ExecutorService pool = new ThreadPoolExecutor(10,20,1L, TimeUnit.SECONDS,
//                new LinkedBlockingDeque<>(3), Executors.defaultThreadFactory(), new ThreadPoolExecutor.CallerRunsPolicy());
//        final CountDownLatch endGate = new CountDownLatch(n);


//        StopWatch clock = new StopWatch();
//        clock.start("multiThread");
        // 用 id 遍历数据集，遍历过程中，首先依据函数调用时刻与上次调用的差值（调用间隔）来选择组件，而后按照策略返回
        for(int id=0;id<n;id++){
            int[] timeSeries = data.get(id)[0];
            int[] numberSeries = data.get(id)[1];
            int finalId = id;
//            System.out.println(Arrays.toString(timeSeries));
//            Runnable task = () -> {
                try{
                    if(finalId%(n/100)==0) System.out.println("here is " + finalId + ", which is " + finalId/(n/100));       // 输出进度

//                    System.out.println("[1] " + Thread.currentThread().getName()+"----"+ finalId +" " +Arrays.toString(timeSeries));
                    // 遍历该函数所有的调用记录
                    for(int i=0;i<timeSeries.length;i++){
                        // 先判断此次调用是否是冷启动
                        // 根据当前调用时刻和访问量，更新直方图
                        MyFunction myFunction = updateFuncHistogram(finalId, timeSeries[i], numberSeries[i]);
                        // 如果当前函数没有过多 OOB
                        if(myFunction.getOOBTimes() <= OOBThreshold){
                            // 计算直方图 cv 来衡量是否具有代表性
                            double cov = getCoV(myFunction.getHistogram());

                            if(cov<COVThreshold){
                                // 直方图尚未具有代表性，标准保活方法
                                standardKeepalivePolicy(myFunction);
                            }else{
                                // 直方图具有代表性，直方图策略
                                histogramPolicy(myFunction);
                            }
                        }else{
                            // 存在过多的越界，时间序列模型
                            timeSeriesPredictionPolicy(myFunction, i, timeSeries);
                        }
                    }

                }catch (Exception e) {
                    e.printStackTrace();

                }finally {
//                    endGate.countDown();
                }

//            };
//            task.run();
//            pool.execute(task);
            System.out.println("funcId="+finalId+" done");

        }

//        clock.stop();
//        try {
//            endGate.await();
//        } catch (InterruptedException e) {
//            e.printStackTrace();
//        }
//        pool.shutdown();

        System.out.println("All done!");
//        System.out.println(clock.prettyPrint());

    }
    /**
     * 判断此次调用是否是冷启动，并记录相关信息
     * @param funcId
     * @param arrivalTime
     * @param arrivalNumber
     * @return void
     * @author Seepen
     * @creed: Talk is cheap,show me the code
     * @date 2022/8/19 11:23
     */
    void recordColdStart(int funcId, int arrivalTime, int arrivalNumber){

        MyFunction myFunction = allFuncMap.get(funcId);

        if(myFunction.getOOBTimes() > OOBThreshold){

            if(arrivalTime >= myFunction.getPreWarm()) handleMemoryWasted(funcId, arrivalTime, arrivalNumber, 1);      // 浪费内存时间计算
            // 如果OOB过阈值了，有用过时间序列模型预测，则判断冷启动时前后区间意义就变了，需额外判断
            if(arrivalTime >= myFunction.getPreWarm() && arrivalTime <= myFunction.getKeepAlive()){
                myFunction.setWarmStartTime(myFunction.getWarmStartTime()+1);
//                System.out.println("good prediction");
            }else{
                myFunction.setColdStartTime(myFunction.getColdStartTime()+1);
            }
        }else {
            // OOB正常的情况下，判断冷启动
            int cur = arrivalTime - myFunction.getLastInvocTime();        // 与上次调用的时间间隔

            if (cur >= myFunction.getPreWarm()) handleMemoryWasted(funcId, arrivalTime, arrivalNumber, 0);         // 浪费内存时间计算

            // 如果本次调用与上次调用时刻一致，说明是updateHistogram里初始化的，第一次调用，是冷启动
            // 0----pw____ka----range  只有 pw到ka 这一段是暖启动
            if (arrivalTime == myFunction.getLastInvocTime() || (cur > 0 && cur < myFunction.getPreWarm()) || cur > myFunction.getKeepAlive()) {
                myFunction.setColdStartTime(myFunction.getColdStartTime() + 1);
//            List<Integer> list = new ArrayList<>(); // 冷启动时刻、上一次调用时刻、冷启动时预热保活窗口值
//            list.add(arrivalTime);
//            list.add(myFunction.getLastInvocTime());
//            list.add(myFunction.getPreWarm());
//            list.add(myFunction.getKeepAlive());
//            if(myFunction.getColdStartList()==null) myFunction.setColdStartList(new ArrayList<List<Integer>>());
//            myFunction.getColdStartList().add(list);
            } else {
                myFunction.setWarmStartTime(myFunction.getWarmStartTime() + 1);

            }
        }
    }
    /**
     * 计算此次调用之前浪费了多少内存时间，mw = arrTime > keepalive ? arrTime-prewarm : keep - pre
     * 仅支持落在 prewarm 之后的调用的计算。若在之前，则直接冷启动去了
     * @param funcId
    	 * @param arrivalTime
    	 * @param arrivalNumber
     * @return void
     * @author Seepen
     * @creed: Talk is cheap,show me the code
     * @date 2022/10/12 17:15
     */
    void handleMemoryWasted(int funcId, int arrivalTime, int arrivalNumber, int isOOB){
        MyFunction myFunction = allFuncMap.get(funcId);
        int memTime = 0;
        if(isOOB==0) memTime = Math.min(arrivalTime-myFunction.getLastInvocTime(), myFunction.getKeepAlive()) - myFunction.getPreWarm();
        else memTime = Math.min(arrivalTime, myFunction.getKeepAlive()) - myFunction.getPreWarm();
        myFunction.setMemoryWasted(myFunction.getMemoryWasted() + memTime);

    }

    MyFunction fixHistogram(int funcId, int arrivalTime, int arrivalNumber) {

        // 当函数第一次调用，尚未拥有管理对象时，先创建对象加到map中
        // 只有一次调用，因此直方图不需更新，只需更新上次调用时刻即可
        if (!allFuncMap.containsKey(funcId)) {
            // 创建实例
            MyFunction myFunction = new MyFunction(funcId, histogramRange);
            myFunction.setLastInvocTime(arrivalTime);
//            myFunction.setColdStartTime(1);
            myFunction.getOOBSeries().add(arrivalTime);
            allFuncMap.put(funcId, myFunction);
            // 记录冷启动，针对首次调用，判断上次调用与此次调用相等为冷启动
            recordColdStart(funcId, arrivalTime, arrivalNumber);
            return myFunction;
        }

        // 记录冷启动
        recordColdStart(funcId, arrivalTime, arrivalNumber);
        MyFunction myFunction = allFuncMap.get(funcId);
        myFunction.setLastInvocTime(arrivalTime);
        return myFunction;
    }

    /**
     * 根据调用更新直方图，传入函数id以及此函数此次调用时刻，获取函数管理对象，更新直方图。
     * 同时判断是否是冷启动
     * @param funcId
     * @param arrivalTime
     * @return void
     * @author Seepen
     * @creed: Talk is cheap,show me the code
     * @date 2022/8/16 20:34
     */
    MyFunction updateFuncHistogram(int funcId, int arrivalTime, int arrivalNumber){

        // 当函数第一次调用，尚未拥有管理对象时，先创建对象加到map中

        if(! allFuncMap.containsKey(funcId)) {

            MyFunction myFunction = new MyFunction(funcId, histogramRange);             // 创建实例
            myFunction.setLastInvocTime(arrivalTime);           // 只有一次调用，因此直方图不需更新，只需更新上次调用时刻即可
            myFunction.getOOBSeries().add(arrivalTime);
            allFuncMap.put(funcId, myFunction);

            recordColdStart(funcId, arrivalTime, arrivalNumber);        // 记录冷启动，针对首次调用，判断上次调用与此次调用相等为冷启动
            return myFunction;
        }

        // 记录冷启动或暖启动
        recordColdStart(funcId, arrivalTime, arrivalNumber);

        // 对有过调用记录的函数
        MyFunction myFunction = allFuncMap.get(funcId);
        int lastInvoc = myFunction.getLastInvocTime();
        myFunction.setLastInvocTime(arrivalTime);

        // 先判断此次调用时间间隔是否超出直方图范围
        if(arrivalTime - lastInvoc >= histogramRange){

            myFunction.setOOBTimes(myFunction.getOOBTimes()+1);                     // OOB次数加一
//            if(myFunction.getOOBSeries()==null) myFunction.setOOBSeries(new ArrayList<>());     // OOB序列添加元素
//            myFunction.getOOBSeries().add(arrivalTime);

        }else{
            // 更新直方图
            myFunction.getHistogram()[arrivalTime-lastInvoc] += arrivalNumber;
            // OOB次数减一
            myFunction.setOOBTimes(myFunction.getOOBTimes()>0?myFunction.getOOBTimes()-1:0);
//            myFunction.setOOBTimes(0);
        }


        //// OOB时间序列要在每次调用时都记录。这么做是为了时序预测建模时数据足够多。但不必单独储存啊，传当前

        return myFunction;
    }

    /**
     * 根据传进来的函数管理实例，拿到直方图，更新窗口值
     * @param myFunction
     * @return void
     * @author Seepen
     * @creed: Talk is cheap,show me the code
     * @date 2022/8/18 11:00
     */
    void histogramPolicy(MyFunction myFunction){
        int[] histogram = myFunction.getHistogram();
        int sum=0;
        int pointer=0, head=0;                       // 头尾标志位
        for(int v : histogram)
            if(v>0)    sum+=v;                      // 直方图中总启动数
        for(int i=0;i<histogramRange;i++){
            pointer+=histogram[i];                  // 当前累加启动数
            if(head == 0 && pointer >= sum*headPercentageThreshold){      // 寻找头指针，若累加数已大于头部阈值，设置prewarm窗口
                head=1;
                myFunction.setPreWarm(i==0?0:i-1);
            }
            if(pointer >= sum*tailPercentageThreshold){         // 寻找尾指针，此时头指针已寻得。若累加数到达尾部阈值，设置keepalive窗口
                myFunction.setKeepAlive(i);
                break;
            }
        }
    }

    /**
     * 标准保活策略
     * @param myFunction
     * @return void
     * @author Seepen
     * @creed: Talk is cheap,show me the code
     * @date 2022/8/18 15:42
     */
    void standardKeepalivePolicy(MyFunction myFunction){
        myFunction.setPreWarm(0);
        myFunction.setKeepAlive(histogramRange);

    }
    /**
     * 时间序列预测组件
     * @param myFunction
     * @return void
     * @author Seepen
     * @creed: Talk is cheap,show me the code
     * @date 2022/8/19 9:59
     */
    void timeSeriesPredictionPolicy(MyFunction myFunction, int cur, int[] series) throws IOException {
        int[] preSeries = Arrays.copyOf(series, cur+1);
        int res = invokePython("arima", preSeries);
        myFunction.setNextInvoc(res);       // 预测的下一次时刻
        myFunction.setPreWarm(Math.max(res-120, myFunction.getLastInvocTime()));        // 此时pre和keep的意义就变为预测时刻的上下限，而不是直方图范围了
        myFunction.setKeepAlive(res+120);

    }

    /**
     * 计算变异系数
     * @param array
     * @return double
     * @author Seepen
     * @creed: Talk is cheap,show me the code
     * @date 2022/8/18 11:38
     */
    double getCoV(int[] array){
        double n = array.length;
        if(n==0)    return 0;

        double sum = 0;
        for (int value : array) {
            sum += value;      //求出数组的总和
        }
        double average = sum / n;  //求出数组的平均数

        double variance=0;
        for (int value : array) {
            variance += Math.pow((value - average),2);   //求出方差
        }
        double standardDeviation = Math.sqrt(variance/n);   //求出标准差
        double CoV = standardDeviation/average; // 变异系数
        return CoV;
    }

    /**
     * 统计冷启动情况
     * @param map
     * @return double[]
     * @author Seepen
     * @creed: Talk is cheap,show me the code
     * @date 2022/8/19 16:48
     */
    double[] coldStartStatistic(Map<Integer, MyFunction> map){
        double[] res = new double[3]; // 冷启动数、暖启动数、平均冷启动率
        double[] rates = new double[map.size()];
        File writeResult = new File("src\\dataSet\\newTest_func_result_1-7_days_cov=4.csv");
        try {
            BufferedWriter writer = new BufferedWriter(new FileWriter(writeResult));

            for (int i : map.keySet()) {
                MyFunction myFunction = map.get(i);
                double cold = (double) myFunction.getColdStartTime();
                double warm = (double) myFunction.getWarmStartTime();
//                System.out.printf("[%f], [%f]\n", cold, warm);
                if(cold+warm == 1) {
//                    System.out.println("mmm");
                    continue;
                }
                res[0] += cold;
                res[1] += warm;
                rates[i] = cold / (cold + warm);
                double cov = getCoV(myFunction.getHistogram());

                writer.write(""+rates[i] + ","+ myFunction.getMemoryWasted() + ","+ myFunction.getMemoryWasted()/(cold+warm)+"," + cov + HashOwners.get(i) +","+HashFunctions.get(i));
//                writer.write("" + cov);
                writer.newLine();
//            System.out.println(rates[i]);

            }
            writer.flush();
            writer.close();
        }catch (Exception e){
            e.printStackTrace();
        }
//        double r=0;
//        for(double i : rates) r+=i;
        res[2] = res[0] / (res[1]+res[0]);
        Arrays.sort(rates);
        System.out.println(Arrays.toString(rates));

        return res;
    }



}
