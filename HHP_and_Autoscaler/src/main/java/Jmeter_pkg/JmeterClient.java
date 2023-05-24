package Jmeter_pkg;


import Cold_Start_Strategy.MyFunction;
import lombok.Data;
import org.apache.jmeter.JMeter;
import org.apache.jmeter.control.LoopController;
import org.apache.jmeter.engine.StandardJMeterEngine;
import org.apache.jmeter.protocol.http.control.HeaderManager;
import org.apache.jmeter.protocol.http.sampler.HTTPSamplerProxy;
import org.apache.jmeter.report.config.ConfigurationException;
import org.apache.jmeter.report.dashboard.GenerationException;
import org.apache.jmeter.reporters.ResultCollector;
import org.apache.jmeter.reporters.Summariser;
import org.apache.jmeter.reporters.SummariserRunningSample;
import org.apache.jmeter.testelement.TestElement;
import org.apache.jmeter.testelement.TestPlan;
import org.apache.jmeter.threads.ThreadGroup;
import org.apache.jmeter.util.JMeterUtils;
import org.apache.jorphan.collections.HashTree;

import java.io.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Objects;

@Data
public class JmeterClient {

	private static final String JMETER_REPORT_OUTPUT_DIR_PROPERTY = "";
	static String gatewayProxyIP = "192.168.103.101";
	static int gatewayProxyPort = 30754;

	String jmeterHomeString = "D:\\Seepen\\ACMIS\\MyGraduation\\project_work\\apache-jmeter-5.4.3";

	public JmeterClient(){}

	/**
	 *
	 * @param testUrl 待测试url
	 * @param postBody postBody
	 * @param concurrencyNum 线程数
	 * @param rampUp 时间
	 * @param target 当前Ksvc并发配置
	 * @param reportPath 报告输出路径
	 * @return
	 */
	public ArrayList<String> executePlan(String testUrl, String postBody, int concurrencyNum, int rampUp, int target, int util, String reportPath) {

		ArrayList<String> res = new ArrayList<>();

		File jmeterHome = new File(jmeterHomeString);
		String slash = System.getProperty("file.separator");
		JMeterUtils.setJMeterHome(jmeterHomeString);

		// jemter 引擎
		StandardJMeterEngine standardJMeterEngine = new StandardJMeterEngine();
		// 设置不适用gui的方式调用jmeter
		System.setProperty(JMeter.JMETER_NON_GUI, "true");
		// 设置jmeter.properties文件，我们将jmeter文件存放在resources中，通过classload
		String path = Objects.requireNonNull(JmeterClient.class.getClassLoader().getResource("jmeter.properties")).getPath();

//		File jmeterPropertiesFile = new File(path);
		File jmeterPropertiesFile = new File(jmeterHome.getPath() + slash + "bin" + slash + "jmeter.properties");

		if (jmeterPropertiesFile.exists()) {
			//JMeter initialization (properties, log levels, locale, etc)
			JMeterUtils.setJMeterHome(jmeterHome.getPath());
			JMeterUtils.loadJMeterProperties(jmeterPropertiesFile.getPath());
			JMeterUtils.initLogging();// you can comment this line out to see extra log messages of i.e. DEBUG level
			JMeterUtils.initLocale();

//			JMeterUtils.loadJMeterProperties(jmeterPropertiesFile.getPath());
			HashTree testPlanTree = new HashTree();
			// 创建测试计划
			TestPlan testPlan = new TestPlan("Create JMeter Script From Java Code");
			// 创建http请求收集器
			HTTPSamplerProxy examplecomSampler = createHTTPSamplerProxy(testUrl, postBody);
			// 创建循环控制器
			LoopController loopController = createLoopController();
			// 创建线程组
			ThreadGroup threadGroup = createThreadGroup(concurrencyNum, rampUp);
			// 线程组设置循环控制
			threadGroup.setSamplerController(loopController);
			// 将测试计划添加到测试配置树种
			HashTree threadGroupHashTree = testPlanTree.add(testPlan, threadGroup);
			// 将http请求采样器添加到线程组下
			threadGroupHashTree.add(examplecomSampler);

			//增加结果收集
			Summariser summary = null;
			String summariserName = JMeterUtils.getPropDefault("summariser.name", "summary");
			if (summariserName.length() > 0) {
				summary = new Summariser(summariserName);
			}


			System.out.println("target=" + target + " summary is");
			String logFile = reportPath + "_result_"+target+"_"+ System.currentTimeMillis() +".jtl";
			ResultCollector logger = new ResultCollector(summary);
			logger.setFilename(logFile);
			testPlanTree.add(testPlanTree.getArray(), logger);


			// 配置jmeter
			standardJMeterEngine.configure(testPlanTree);
			// 运行
			long startTime = System.currentTimeMillis();
			standardJMeterEngine.run();
			long endTime = System.currentTimeMillis();
			SummariserRunningSample total = summary.getTotal();

			// 返回测试结果
			res.add(String.valueOf(target));
			res.add(String.valueOf(util));
			res.add(String.valueOf(total.getRate()));
			res.add(String.valueOf(total.getAverage()));
			res.add(getP90Line(logFile, concurrencyNum));
			res.add(String.valueOf(total.getMin()));
			res.add(String.valueOf(total.getMax()));
			res.add(String.valueOf(total.getErrorCount()));
			res.add(String.valueOf(startTime));
			res.add(String.valueOf(endTime));

			System.out.println(Arrays.toString(res.toArray()));

		}

		return res;
	}

	/**
	 * 创建线程组
	 *
	 * @return
	 */
	public ThreadGroup createThreadGroup(int threadNum, int rampUp) {
		ThreadGroup threadGroup = new ThreadGroup();
		threadGroup.setName("Example Thread Group");
		threadGroup.setNumThreads(threadNum);
		threadGroup.setRampUp(rampUp);

		threadGroup.setProperty(TestElement.TEST_CLASS, ThreadGroup.class.getName());
		threadGroup.setScheduler(true);
		threadGroup.setDuration(1);
		threadGroup.setDelay(0);
		return threadGroup;
	}

	/**
	 * 创建循环控制器
	 *
	 * @return
	 */
	public LoopController createLoopController() {
		// Loop Controller
		LoopController loopController = new LoopController();
		loopController.setLoops(1);
		loopController.setContinueForever(true);
		loopController.setProperty(TestElement.TEST_CLASS, LoopController.class.getName());
		loopController.initialize();
		return loopController;
	}

	/**
	 * 创建http采样器
	 *
	 * @return
	 */
	public HTTPSamplerProxy createHTTPSamplerProxy(String testUrl, String postBody) {
		HeaderManager headerManager = new HeaderManager();
		headerManager.setProperty("Content-Type", "multipart/form-data");
		HTTPSamplerProxy httpSamplerProxy = new HTTPSamplerProxy();

		httpSamplerProxy.setProperty("HTTPSampler.proxyHost", gatewayProxyIP);
		httpSamplerProxy.setProperty("HTTPSampler.proxyPort", gatewayProxyPort);

		httpSamplerProxy.setDomain(testUrl);
		httpSamplerProxy.setPort(80);
		httpSamplerProxy.setPath("/");

		httpSamplerProxy.setMethod("POST");
		httpSamplerProxy.setPostBodyRaw(true);
		httpSamplerProxy.addNonEncodedArgument("", postBody, "");

		httpSamplerProxy.setUseKeepAlive(true);
		httpSamplerProxy.setProperty(TestElement.TEST_CLASS, HTTPSamplerProxy.class.getName());
		httpSamplerProxy.setHeaderManager(headerManager);

		return httpSamplerProxy;
	}


	/**
	 * 计算响应延迟的 P90 分位
	 * @param path
	 * @param concur
	 * @return
	 */
	public String getP90Line(String path, int concur){
		int[] latency = new int[concur];

		try {
			BufferedReader reader = new BufferedReader(new FileReader(path));
			String line = null;
			int index = 0;
			while ((line = reader.readLine()) != null) {
				// 跳过首行字段
				if (index == 0) {
					index++;
					continue;
				}
				String[] item = line.split(",");
				latency[index-1] = Integer.parseInt(item[1]);
				index++;
			}

		}catch (Exception e){
			e.printStackTrace();
		}

		Arrays.sort(latency);
//		System.out.println(Arrays.toString(latency));
		return String.valueOf(latency[concur/10 * 9]);

	}

}
