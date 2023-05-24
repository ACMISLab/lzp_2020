import Jmeter_pkg.JmeterClient;
import QLearning.AutoscaleController;

import java.util.ArrayList;

public class ResultSummary {
	String reportPath = "D:\\Seepen\\ACMIS\\MyGraduation\\cold-2\\src\\main\\java\\Jmeter_report";
	JmeterClient jmeterClient = new JmeterClient();
	AutoscaleController autoscaleController = new AutoscaleController();

	public void appendP90Line(int ccur, int round){
		ArrayList<ArrayList<String>> file = new ArrayList<>();
		String dictPath = reportPath + "\\ccur="+ccur+"\\round_"+round;
		for(int i=10;i<200;i+=10){
			String path = dictPath+"\\result_"+i+".jtl";
			String res = jmeterClient.getP90Line(path, ccur);
			ArrayList<String> line = new ArrayList<>();
			line.add(res);
			file.add(line);
		}

		autoscaleController.write2Csv(dictPath+"\\latencyP90_all.csv", file);


	}
	public static void main(String[] args) {
		ResultSummary resultSummary = new ResultSummary();

		for(int c=200;c<500;c+=100){
			for(int r=1;r<6;r++){
				resultSummary.appendP90Line(c, r);
			}
		}




	}
}
