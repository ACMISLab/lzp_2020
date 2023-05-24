package Cold_Start_Strategy;

import lombok.Getter;
import lombok.Setter;

import java.util.ArrayList;
import java.util.List;

// 函数类
@Setter
@Getter
public class MyFunction {
    //    String name;
    private int id;
    private int[] histogram;    // 直方图数据结构，下标为分钟
    private List<Integer> OOBTimeList;
    private int lastInvocTime = -1; // 函数上次调用时刻
    private int OOBTimes = 0;       // 越界次数
    private List<Integer> OOBSeries = new ArrayList<Integer>();       // 越界时刻时间序列，供时序预测模型使用
    private int preWarm = 0;    // 预热窗口期w为多大（从0到w）
    private int keepAlive = 0;  // 保活窗口期k（从w到k）
    private int nextInvoc = 0;  // 预测下一次调用时刻（之后的第n分钟）
    private int aliveContainerNum = 1;  // 保活实例数
    private int coldStartTime=0;        // 冷启动次数
    private int warmStartTime=0;        // 暖启动次数
    private List<List<Integer>> coldStartList;  //  记录冷启动时信息，冷启动时刻、上一次调用时刻、冷启动时预热保活窗口值
    private int memoryWasted=0;         // 内存浪费时间

    MyFunction(){}
    MyFunction(int _id){id = _id;}
    MyFunction(int _id, int histRange){
        id = _id;
        histogram = new int[histRange];
        keepAlive = histRange;
    }
}
