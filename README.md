# FaceDataSets_Manual_Annotation_Tools
Face attributes manual annotatior python tool projects

## 该工程主要包含人脸三种属性的手动标注工具

### LandmarksAnnotation（人脸关键点手动标注工具）
#### 通过已有人脸检测和关键点检测模型推理并可视化标注出对应人脸图片人脸68关键点位置，手动调整不准确关键点的位置，根据调整的坐标自动更新标签文件
### OcclusionAnnotation（人脸遮挡手动标注工具）
#### 显示待标注人脸图片，通过观察人脸遮挡情况手动标注出人脸七个区域的遮挡属性（0表示未遮挡，1表示遮挡）
### PoseAnnotation（人脸姿态手动标注工具）
#### 显示待标注人脸图片，通过观察人脸姿态情况手动标注出人脸3个方向的角度值（标注值范围：0~90）