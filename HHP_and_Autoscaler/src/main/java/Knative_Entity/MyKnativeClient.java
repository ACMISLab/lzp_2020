package Knative_Entity;

import io.fabric8.knative.client.DefaultKnativeClient;
import io.fabric8.knative.client.KnativeClient;
import io.fabric8.knative.serving.v1.Service;
import io.fabric8.knative.serving.v1.ServiceBuilder;
import io.fabric8.kubernetes.client.Config;
import io.fabric8.kubernetes.client.ConfigBuilder;
import lombok.Data;

import java.util.HashMap;
import java.util.Map;

@Data
public class MyKnativeClient {

	private final String masterUrl = "https://192.168.103.100:6443/";
	private final Config config;
	private final KnativeClient kn;

	public MyKnativeClient(){
		config = new ConfigBuilder()
				.withMasterUrl(masterUrl)
				.withTrustCerts(true)
				.build();
		kn = new DefaultKnativeClient(config).adapt(KnativeClient.class);
	}


	/**
	 * 对现有 Ksvc ,更新其 revision
	 * 目前仅先支持修改配置，即 annotation 中的设置
	 */
	public Service updateKsvc(String namespace, String ksvName, Map<String, String> paramsMap){
		Map<String, String> annoMap = new HashMap<>();
		/**
		 * 定义指标，可选 rps，默认 concurrency
		 */
		if(paramsMap.containsKey("metric")){
			annoMap.put("autoscaling.knative.dev/metric", paramsMap.get("metric"));
		}
		/**
		 * 定义所选指标的扩容阈值，默认 100，一般 0-200
		 */
		if(paramsMap.containsKey("target")) {
			annoMap.put("autoscaling.knative.dev/target", paramsMap.get("target"));
		}
		/**
		 * 定义 hard limit 时的资源利用率
		 */
		if(paramsMap.containsKey("utilization") && paramsMap.containsKey("hardLimit")) {
			annoMap.put("autoscaling.knative.dev/target-utilization-percentage", paramsMap.get("utilization"));
		}
		/**
		 * 如果用户有指定hardLimit，将其指定出来
		 */
		Long hardLimit = paramsMap.containsKey("hardLimit") ? Long.parseLong(paramsMap.get("hardLimit")) : Long.parseLong(paramsMap.get("target")) + 100;

		/**
		 * 根据配置更新 Ksvc
		 */
		Service res = kn.services().inNamespace(namespace).withName(ksvName)
				.edit(service -> new ServiceBuilder(service)
						.editSpec()
							.editTemplate()
								.editMetadata()
									.withAnnotations(annoMap)
								.endMetadata()
								.editSpec()
									.withContainerConcurrency(hardLimit)
								.endSpec()
							.endTemplate()
						.endSpec()
						.build());

		return res;

	}

}
