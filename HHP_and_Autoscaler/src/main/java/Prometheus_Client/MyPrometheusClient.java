package Prometheus_Client;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

public class MyPrometheusClient {
	public String proIP = "192.168.103.100";
	public int proPort = 9090;

	String ClusterMemoryBaseQuery = "%28node_memory_MemTotal_bytes-%28node_memory_MemFree_bytes%2B+node_memory_Cached_bytes+%2B+node_memory_Buffers_bytes%29%29%2Fnode_memory_MemTotal_bytes+*+100";
	String ClusterCPUBaseQuery = "100+*+%281+-+sum+by+%28instance%29%28increase%28node_cpu_seconds_total%7Bmode%3D%22idle%22%7D%5B1m%5D%29%29+%2F+sum+by+%28instance%29%28increase%28node_cpu_seconds_total%5B1m%5D%29%29%29";
	String ClusterNetworkBaseQuery = "";
	String ClusterDiskBaseQuery = "";

	public MyPrometheusClient(){ }

	public String getPodCPUQuery(String ksvcName, long timeMillis){
		String startTime = String.valueOf(timeMillis);
		String endTime = String.valueOf(timeMillis+1000);
		return "sum%28irate%28container_cpu_usage_seconds_total%7Bimage%21%3D%22%22%2C+name%3D%7E%22.*user-container_" + ksvcName + ".*%22%2C+name%21%7E%22.*POD.*%22%7D%5B1m%5D%29*100%29by%28name%29+%2F+sum%28100000%2Fcontainer_spec_cpu_period%7Bimage%21%3D%22%22%2Cname%3D%7E%22.*user-container_"+ksvcName+".*%22%2C+name%21%7E%22.*POD.*%22%7D%29by%28name%29&start="+startTime+"&end="+endTime+"&step=1";

	}

	public String getClusterFullQuery(String query, long timeMillis){
		String startTime = String.valueOf(timeMillis);
		String endTime = String.valueOf(timeMillis+1000);
		return query+"&start="+startTime+"&end="+endTime+"&step=10";
	}

	public JSONObject sendQuery(String query, long timeMillis) throws IOException {

		String url = "http://" + proIP +":"+ proPort +"/api/v1/query?query=" + getClusterFullQuery(query, timeMillis);
		HttpGet get = new HttpGet(url);
		CloseableHttpClient httpClient = HttpClients.custom().build();
		CloseableHttpResponse response = httpClient.execute(get);
		String s = EntityUtils.toString(response.getEntity());
		//		System.out.println(jsonObject.toJSONString());
		return JSONObject.parseObject(s);

	}



	public List<Double> getSystemInfo(long time) throws IOException {
		List<Double> res = new ArrayList<>();

		JSONObject cpuInfo = sendQuery(ClusterCPUBaseQuery, time);
		JSONArray cpuArray = cpuInfo.getJSONObject("data").getJSONArray("result");
		double cpuAvg = getAvgCPU(cpuArray);
		res.add(cpuAvg);

		JSONObject memInfo = sendQuery(ClusterMemoryBaseQuery, time);
		JSONArray memArray = memInfo.getJSONObject("data").getJSONArray("result");
		double memAvg = getAvgMemory(memArray);
		res.add(memAvg);

		return res;

	}

	public double getAvgMemory(JSONArray jsonArray){
		double res = 0;
		for (int i=0; i<jsonArray.size(); i++){
			JSONObject jsonObject = jsonArray.getJSONObject(i);
			String str = jsonObject.getJSONArray("value").get(1).toString();
			double v = Double.parseDouble(str);
			res += v;
		}
		return res / jsonArray.size();
	}

	public double getAvgCPU(JSONArray jsonArray){
		double res = 0;
		for (int i=0; i<jsonArray.size(); i++){
			JSONObject jsonObject = jsonArray.getJSONObject(i);
			JSONArray arrayList = (JSONArray) jsonObject.get("value");
			double v = Double.parseDouble((String) arrayList.get(1));
			res += v;
		}
		return res / jsonArray.size();
	}

	public static void main(String[] args) throws IOException,InterruptedException {
		MyPrometheusClient myPrometheusClient = new MyPrometheusClient();
		String ksvc = "floating";
		long time = System.currentTimeMillis();

//		JSONObject res = myPrometheusClient.getSystemInfo(time);
//
//		System.out.println(res.get("cpu"));
//		System.out.println(res.get("mem"));

	}
}
