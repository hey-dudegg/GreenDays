import pandas as pd
import numpy as np
import os
import tensorflow as tf
from tensorflow.keras import Model
import csv
import sklearn
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split


aq = pd.read_csv(os.path.join('/home/joljak/AQ_home_prac.csv'), encoding='utf8')

# 데이터 전처리(누락치, 이상치 보정, 불필요 특성 제거)
med_pm2_5 = aq[aq["PM"] != 0]["PM"].median()
med_co2 = aq[aq["CO2"] != 0]["CO2"].median()
# med_tvoc = aq[aq["tvoc"] != 0]["tvoc"].median()
aq.loc[aq["CO2"] == 0, "CO2"] = med_co2 # 누락된값()을 median 값으로, 0을 제외한 값 중 median.
aq.loc[aq["PM"] == 0, "PM"] = med_pm2_5
aq.loc[aq["PM"] > 70, "PM"] = 70 # 어린이집 유지기준 35이하 *2
aq.loc[aq["Voc"] > 800, "Voc"] = 70 # 어린이집 유지기준 400이하 *2
# aq.loc[aq["co2"] > 2000, "co2"] = 2000 # 어린이집 유지기준 1000이하 *2


# Min-MaxScaler 선언
scaler = MinMaxScaler()
scaler_pred = MinMaxScaler()
scale_cols = ['Voc', 'CO', 'CO2']
scale_cols_pred = ['PM']

# 스케일 후 columns
scaled = scaler.fit_transform(aq[scale_cols])
scaled_pred = scaler_pred.fit_transform(aq[scale_cols_pred])
df = pd.DataFrame(scaled, columns=scale_cols)
df2 = pd.DataFrame(scaled_pred, columns=scale_cols_pred)
df = pd.concat([df, df2], axis=1)

x_train, x_test, y_train, y_test = train_test_split(df.drop('PM', axis = 1), df['PM'], test_size=0.2, random_state=0, shuffle=False)


WINDOW_SIZE=5
BATCH_SIZE=30

def windowed_dataset(x, y, window_size, batch_size):
    # X값 window dataset 구성
    ds_x = tf.data.Dataset.from_tensor_slices(x) # tensor를 2,의 크기로 하나씩 자른다. 총 (2,)의 텐서가 12,653개 생김
    ds_x = ds_x.window(WINDOW_SIZE, shift=1, drop_remainder=True) # 1개씩 밀어가며 30개씩 데이터를 얻는다. drop_remainder는 끝에 데이터셋을 초과하지 않도록
    ds_x = ds_x.flat_map(lambda x: x.batch(WINDOW_SIZE)) # data를 flat하게 보여줌 30개의 1차원 텐서가 생성됨. 차원을 낮춘다. batch()는 데이터의 크기를 결정, 메모리에 30개씩 올린다.
    ds_y = tf.data.Dataset.from_tensor_slices(y[WINDOW_SIZE:])
    ds = tf.data.Dataset.zip((ds_x, ds_y)) # zip()함수로 x와 y을 묶어준다.
    return ds.batch(batch_size).prefetch(1) # prefatch: 미리 데이터를 fetch하는 개수. 병렬 처리로 학습 속도 개선


# trian_data는 학습용 데이터셋, test_data는 검증용 데이터셋
train_data = windowed_dataset(x_train, y_train, WINDOW_SIZE, BATCH_SIZE)
test_data = windowed_dataset(x_test, y_test, WINDOW_SIZE, BATCH_SIZE)


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Conv1D, Lambda, GRU
from tensorflow.keras.losses import Huber
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

WINDOW_SIZE=5
BATCH_SIZE=30

# GRU 모델 구현.
model = Sequential([
   Conv1D(filters=32, kernel_size=5, 
          padding="causal", # 한쪽 방향으로 얼마만큼 띄어서 padding할 것인가.(Default:0)
          activation="relu", # 활성화 함수
          input_shape=[WINDOW_SIZE, 3]),
    GRU(units = 64, return_sequences = True),
    GRU(units = 64, return_sequences = True),
    GRU(units = 64, activation='tanh'),
    Dense(64, activation="relu"),
    Dense(1),
])

loss = Huber() # Sequence 학습에 비교적 좋은 퍼포먼스를 내는 Huber()를 사용
optimizer = Adam(0.00005) # Adam : 최적화 함수
model.compile(loss=Huber(), optimizer=optimizer, metrics=['mae'])

# earlystopping은 10번 epoch통안 val_loss 개선이 없다면 학습을 멈춤
earlystopping = EarlyStopping(monitor='val_loss', patience=3)
# val_loss 기준 체크포인터 생성
filename = os.path.join('tmp', 'ckeckpointer.ckpt')
checkpoint = ModelCheckpoint(filename, 
                             save_weights_only=True, 
                             save_best_only=True, 
                             monitor='val_loss', 
                             verbose=1)

history = model.fit(train_data, 
                    validation_data=(test_data), 
                    batch_size=BATCH_SIZE,
                    epochs=50, 
                    callbacks=[checkpoint, earlystopping])

model.load_weights(filename)
pred = model.predict(test_data)
pred = scaler_pred.inverse_transform(pred)

pred_df = pd.DataFrame(np.zeros((12446, 1)), columns=['Pred'])  # 0으로 초기화된 DataFrame 생성
pred_df.iloc[:2485, 0] = pred.flatten()

result_df = pd.concat([df, pred_df], axis=1)

# 결과 확인
print(result_df.head())

# 저장
output_path = os.path.join('/home/joljak/AQ_home_prac_saved1.csv')
result_df.to_csv(output_path, encoding='utf8', index=False)

