# Notes about machine plots and labels

## Y axis

### Machines working in other ways

49514138

### Edge case machines (hard to distinguish normal data from anomalies)

49514139

### Normally working machines (in most of plots)

#### 49514136

#### 49514140

## Unlabeled anomalies

### 49514140 X

At least 2023-12-04.

### 49514568 X

At least 2023-08-07.

### 49514571 X

At least 2023-08-14.

### 49514567 Y

At least 2024-03-04.

## Labeled anomalies

### Axis A REIB

My observations show that each longer jump is preceded by a short, low peak. Time series that have been marked as anomalies have short peaks whose value is similar to longer ones.

Files:
230925_49514571_REIB_A.xml
231204_49514571_REIB_A.xml

Detecting higher value in shorter peaks may be a good indicator.

### Axis A

The residuals looks like a sinus wave. From my observations if there is an anomaly, sinus wave is fluctuating and entire statistical time series get higher values.

Files:
090724_49514136_GL_A_F300.xml
090724_49514136_GL_A_F360.xml
090724_49514136_GL_A_F420.xml

From observations based on these above files, I assume I can detect it using threshold or second residuals.
In normal data std is smooth sine wave. In anomaly, it's fluctuating.

Files:
230925_49514571_GL_A_F300.xml
230925_49514571_GL_A_F360.xml
230925_49514571_GL_A_F420.xml

From observations based on these above files, I assume I can detect it using second residuals.
In normal data std is smooth sine wave. In anomaly, it's fluctuating.

### Axis X

Files:
240108_49514579_GL_X_F2000.xml
240108_49514579_GL_X_F4000.xml
240108_49514579_GL_X_F6000.xml

The anomalies are clearly visible.

Files:
240620_49514576_GL_X_F2000.xml
240620_49514576_GL_X_F4000.xml
240620_49514576_GL_X_F6000.xml

In this case, anomalies were in entire time series. It looked normal, but the values were twice as high.
For this case, I should use constant threshold instead of calculating z score.

### Axis Y

Files:
240219_49514576_GL_Y_F2000.xml
240219_49514576_GL_Y_F4000.xml
240219_49514576_GL_Y_F6000.xml

In this case, anomalies were in entire time series. It looked normal, but the values were twice as high.
For this case, I should use constant threshold instead of calculating z score.

Files:
240506_49514579_GL_Y_F2000.xml
240506_49514579_GL_Y_F4000.xml
240506_49514579_GL_Y_F6000.xml

The anomalies are clearly visible.

Files:
240620_49514576_GL_Y_F2000.xml
240620_49514576_GL_Y_F4000.xml
240620_49514576_GL_Y_F6000.xml

In this case, anomalies were in entire time series. It looked normal, but the values were twice as high.
For this case, I should use constant threshold instead of calculating z score.

Files:
240812_49514579_GL_Y_F2000.xml
240812_49514579_GL_Y_F4000.xml
240812_49514579_GL_Y_F6000.xml

The anomalies are clearly visible.

## Qeustions

### Where to detect anomalies?

Most of the labeled anomalies come from GL measurement, few of them from REIB and only for axis A.

### Does machine values come from the same distribution (beside peaks)?

If not, then a threshold value for anomaly has to be created for each machine separately.
