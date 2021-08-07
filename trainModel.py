import time
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import InputLayer, Dense, Dropout, Bidirectional, LSTM
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard

df = pd.read_csv('BTCUSDT_1m.csv')
df = df.drop(index=np.where(pd.isnull(df))[0])
df.dropna(inplace=True)

print(len(df))
df = df.iloc[int(0.8 * len(df)):, :]
print(len(df))
labels = df['Close'].values
df =  df.iloc[:-1, :]
labels = labels[1:]


X = df.to_numpy(dtype=np.float32)
y = labels
X_train, X_test = X[:int(0.9 * len(X)), :], X[int(0.9 * len(X)):, :]
y_train, y_test = y[:int(0.9 * len(y))], y[int(0.9 * len(y)):]
X_scaler = StandardScaler().fit(X_train)
X_train, X_test = X_scaler.transform(X_train), X_scaler.transform(X_test)

joblib.dump(X_scaler, 'X_scaler.pkl')

train_sequences = np.array(list(map(lambda i: X_train[i - 10:i, :], list(range(10, len(X_train) + 1)))))
print(len(train_sequences))
test_sequences = np.array(list(map(lambda i: X_test[i - 10:i, :], list(range(10, len(X_test) + 1)))))
print(len(test_sequences))

y_train, y_test = y_train[9:], y_test[9:]
print(len(y_train), len(y_test))

s1, s2 = np.arange(len(y_train)), np.arange(len(y_test))
np.random.shuffle(s1)
np.random.shuffle(s2)
train_sequences, y_train = train_sequences[s1], y_train[s1]
test_sequences, y_test = test_sequences[s2], y_test[s2]

X_train = np.stack(train_sequences)
X_test = np.stack(test_sequences)
print(np.shape(X_train), np.shape(X_test))

np.save('X_train', X_train)
np.save('y_train', y_train)
np.save('X_test', X_test)
np.save('y_test', y_test)

model = Sequential()
model.add(InputLayer(input_shape=np.shape(X_train)[1:]))

model.add(Bidirectional(LSTM(128)))
model.add(Dropout(0.2))

model.add(Dense(64, activation='relu'))
model.add(Dropout(0.2))

model.add(Dense(1, activation='linear'))

opt = tf.keras.optimizers.Adam(learning_rate=1e-5)
model.compile(
    optimizer=opt,
    loss='MSE',
    metrics=['MAE']
)

print(X_train[:5])
print(model.summary())

path = 'Checkpoints/cp-{epoch:02d}-{val_MAE:.4f}-' + time.strftime("%H-%M-%S-%d-%m-%Y") + '.hdf5'
cp_callback = ModelCheckpoint(path, verbose=1)

log_dir = f'logs/fit-{time.strftime("%H-%M-%S--%d-%m-%Y")}'
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

history = model.fit(
    X_train, y_train, batch_size=32, epochs=100, callbacks=[cp_callback, tensorboard_callback], validation_data=(X_test, y_test)
)


