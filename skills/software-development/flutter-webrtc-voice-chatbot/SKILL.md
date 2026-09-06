---
name: flutter-webrtc-voice-chatbot
description: Build a cross-platform voice chatbot with Flutter + WebRTC + streaming AI (MiniMax/Groq + edge-tts) — real-time bidirectional voice conversation
triggers:
  - voice chatbot
  - flutter webrtc
  - ai phone
  - voip app
  - real-time voice AI
  - streaming voice AI
  - VAD voice activity detection
---

# Flutter WebRTC Voice Chatbot

Build a cross-platform voice chatbot with Flutter + WebRTC + streaming AI — achieves near real-time bidirectional voice conversation (like a normal phone call).

## Architecture

```
┌─────────────┐  WebSocket   ┌──────────────┐   HTTP/WebSocket   ┌──────────────────┐
│  Flutter    │ ──────────►  │  Python      │ ◄──────────────── │  MiniMax API     │
│  App        │  raw audio  │  Server      │   STT + LLM + TTS │  (STT + LLM)     │
│  (VAD+采集) │  ◄───────── │  (port 8765) │ ────────────────► │  edge-tts (TTS)  │
│             │  audio stream│             │  streaming audio   │                  │
└─────────────┘             └──────────────┘                    └──────────────────┘
       │  WebRTC (port 8080)
       └─► Signaling Server (server.js, Node.js) — only for WebRTC setup
```

**Two separate WebSocket connections:**
1. `ws://server:8080` — WebRTC signaling (offer/answer/ICE)
2. `ws://server:8765` — Raw audio streaming for AI processing

## Project Structure

```
voip-ai-phone/
├── lib/main.dart              # Flutter app (WebRTC + WebSocket audio)
├── server/
│   ├── server.js              # WebRTC signaling (Node.js, port 8080)
│   └── agent.py               # AI server (Python, port 8765)
├── pubspec.yaml
└── build/app/outputs/flutter-apk/app-debug.apk
```

## Key Dependencies (pubspec.yaml)

```yaml
dependencies:
  flutter_webrtc: ^0.12.12+hotfix.1   # WebRTC for audio
  permission_handler: ^11.3.1          # Microphone permission
  record: ^6.0.0                        # Audio recording/streaming
  audioplayers: ^6.1.0                  # Audio playback
  audio_session: ^0.1.21                # Audio session management (voice chat mode)
  web_socket_channel: ^3.1.0           # WebSocket client
  path_provider: ^2.1.4
```

## Common Flutter Compilation Errors

### Error: `allowBluetoothA2DP` not found
```dart
// WRONG - this enum value doesn't exist
avAudioSessionCategoryOptions: AVAudioSessionCategoryOptions.allowBluetoothA2DP,

// CORRECT
avAudioSessionCategoryOptions: AVAudioSessionCategoryOptions.allowBluetooth,
```

### Error: `AndroidAudioGainRequestType` not found
```dart
// WRONG
androidAudioFocusGainType: AndroidAudioGainRequestType.gainTransientMayDuck,

// CORRECT
androidAudioFocusGainType: AndroidAudioFocusGainType.gainTransientMayDuck,
```

## Real-time Streaming Architecture (agent.py)

The key to "normal phone call" latency is **streaming everything** — no wait-for-completion:

```python
# 1. VAD: Energy-based voice activity detection
class VAD:
    def __init__(self, sample_rate=16000, energy_threshold=0.02):
        self.sample_rate = sample_rate
        self.energy_threshold = energy_threshold
        self.speech_chunks = deque()
        self.silence_ms = 0

    def process_chunk(self, audio_data: bytes) -> str:
        """Returns: 'speech', 'silence', or 'end_of_speech:<duration_ms>'"""
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        energy = np.sqrt(np.mean(audio_np ** 2))
        chunk_ms = len(audio_np) * 1000 // self.sample_rate

        if energy > self.energy_threshold:
            self.silence_ms = 0
            self.speech_chunks.append((audio_data, chunk_ms))
            self.is_speaking = True
            return 'speech'
        else:
            if self.is_speaking:
                self.silence_ms += chunk_ms
                if self.silence_ms >= VAD_SILENCE_THRESHOLD_MS:
                    speech_audio = b''.join(d for d, _ in self.speech_chunks)
                    total_ms = sum(ms for _, ms in self.speech_chunks)
                    self.speech_chunks.clear()
                    self.silence_ms = 0
                    self.is_speaking = False
                    return f'end_of_speech:{total_ms}'
            return 'silence'

# 2. STT: MiniMax API (HTTP multipart)
async def transcript(self, audio_data: bytes) -> str:
    wav_buffer = self._pcm_to_wav(audio_data, SAMPLE_RATE)
    form = aiohttp.FormData()
    form.add_field('file', wav_buffer.getvalue(), filename='audio.wav', content_type='audio/wav')
    form.add_field('model', 'speech-01-hd')
    form.add_field('language_boost', 'zh')
    # POST to https://api.minimaxi.com/v1/audio/speechToText

# 3. LLM: MiniMax streaming
async def chat_stream(self, text: str, history: list = None) -> str:
    # POST to https://api.minimaxi.com/v1/text/chatcompletion_v2
    # model: MiniMax-M2.7

# 4. TTS: edge-tts streaming — chunks sent as they are generated
async def generate_speech_stream(text: str, output_queue: asyncio.Queue):
    async for chunk in edge_tts.Communicate(text, voice='zh-CN-XiaoxiaoNeural').stream():
        if chunk['type'] == 'audio':
            await output_queue.put(chunk['data'])  # stream each chunk immediately
    await output_queue.put(None)  # end marker
```

### WebSocket Protocol (App ↔ Server)

**App → Server:**
```json
{"type": "audio", "data": "<base64 PCM bytes>", "sampleRate": 16000}
```

**Server → App:**
```json
{"type": "transcript", "text": "用户说的内容"}
{"type": "response", "text": "AI回复内容"}
{"type": "audio", "data": "<base64 MP3 chunk>"}  // TTS chunks streamed live
{"type": "audio_end"}
```

## Audio Session Configuration

For voice chat on mobile, configure AudioSession properly:

```dart
final session = await AudioSession.instance;
await session.configure(AudioSessionConfiguration(
  avAudioSessionCategory: AVAudioSessionCategory.playAndRecord,
  avAudioSessionCategoryOptions: AVAudioSessionCategoryOptions.allowBluetooth,
  avAudioSessionMode: AVAudioSessionMode.voiceChat,
  androidAudioAttributes: AndroidAudioAttributes(
    contentType: AndroidAudioContentType.speech,
    usage: AndroidAudioUsage.voiceCommunication,
  ),
  androidAudioFocusGainType: AndroidAudioFocusGainType.gainTransientMayDuck,
  androidWillPauseWhenDucked: false,
));
```

## Flutter: Audio Recording + Streaming

The `record` package streams audio chunks over WebSocket:

```dart
// 1. Start recording to temp WAV file
_recorder = AudioRecorder();
await _recorder.start(
  const RecordConfig(
    encoder: AudioEncoder.wav,
    sampleRate: 16000,
    numChannels: 1,
  ),
  path: tempFilePath,
);

// 2. VAD: check amplitude periodically
_timer = Timer.periodic(Duration(milliseconds: 100), (timer) async {
  final amp = await _recorder!.getAmplitude();
  final isSpeaking = amp.current > -40.0; // dB threshold
  // Track silence duration to detect end of speech
});

// 3. Send audio chunks to server via WebSocket
_audioChannel?.sink.add(json.encode({
  'type': 'audio',
  'data': base64Encode(audioBytes),
  'sampleRate': 16000,
}));
```

## Python Server Startup (hermes venv)

⚠️ The hermes venv uses **python3.14** (not python3.11). Ensure packages are installed for the correct Python:

```bash
# Install dependencies for the venv's Python version
/home/saber/.venvs/hermes/bin/python -m pip install websockets edge-tts aiohttp numpy

# Start server
/home/saber/.venvs/hermes/bin/python -u agent.py

# Verify port
ss -tlnp | grep 8765
```

## ⚠️ VAD Timer Sends No Audio Chunks — Critical Flutter Bug

**Symptom:** App connects to AI server, VAD timer runs, amplitude detection works, but AI never replies. Agent logs show client connected/disconnected with no audio data received.

**Root Cause:** `_sendAudioChunk()` exists but VAD timer only calls `getAmplitude()` — it never reads from the recorded WAV file and never calls `_sendAudioChunk()`. The timer appears functional (logs show VAD events) but no audio bytes are ever sent.

**Fix:** VAD timer must read from the temp WAV file and call `_sendAudioChunk()`:

```dart
// Track file position to read only NEW audio data
int lastSentPosition = 0;
_timer = Timer.periodic(Duration(milliseconds: 100), (timer) async {
  if (!_isRecording || _recorder == null) return;

  final amp = await _recorder!.getAmplitude();
  final isSpeaking = amp.current > -40.0;
  // ... VAD logic ...

  // Send audio chunk — THIS IS THE MISSING PIECE
  if (_currentRecordFile != null) {
    final file = File(_currentRecordFile!);
    if (await file.exists()) {
      final stat = await file.stat();
      final fileSize = stat.size;
      if (fileSize > 44 && fileSize > lastSentPosition) {
        final raf = await file.open(mode: FileMode.read);
        await raf.setPosition(lastSentPosition);
        final remaining = fileSize - lastSentPosition;
        final bytes = await raf.read(remaining > 32000 ? 32000 : remaining);
        await raf.close();
        lastSentPosition = fileSize;
        if (bytes.isNotEmpty && _audioChannel != null) {
          _sendAudioChunk(Uint8List.fromList(bytes));
        }
      }
    }
  }
});
```

**Required state variable:**
```dart
String? _currentRecordFile;  // set when recorder.start() is called
```

## ⚠️ websockets 16.0 Breaking API Change (Critical)

websockets 16.0 changed the `process_request` callback signature:

```python
# ❌ OLD (websockets < 16.0) — TypeError: 'Request' object is not iterable
async def process_request_verbose(path, request_headers):
    print(f"  [DEBUG] path={path}")
    print(f"  [DEBUG] headers={dict(request_headers)}")  # FAILS — request_headers is a Request object
    return None

# ✅ NEW (websockets >= 16.0) — single request parameter
async def process_request_verbose(request):
    print(f"  [DEBUG] path={request.path}")
    return None
```

**Symptom when broken:** App connects to 8765 but immediately disconnects. `agent.py` logs show:
```
TypeError: 'Request' object is not iterable
opening handshake failed
```
The WebSocket handshake fails silently — App never establishes a connection to the AI server.

**Fix:** Update `process_request` handler to accept single `request` parameter. See `/home/saber/voip-ai-phone/server/agent.py` line 345.

## 交付原则（刚性）

用户说"你来做决定/直接做/不要问"时，**立即停止询问，直接交付成品**。流程：
1. 明确方案 → 直接实现 → 验证 → 交付
2. 不展示中间思考过程
3. 不问"你觉得可以吗"
4. 遇到障碍先自己解决（搜索、尝试、绕行），解决不了再报告

用户偏好"成品"而非"教程"或"选项"。

## Build & Deploy

```bash
# Android build (set SDK path)
export ANDROID_HOME=/home/saber/android-sdk
export ANDROID_SDK_ROOT=/home/saber/android-sdk
flutter build apk --debug

# Send APK via WeChat when ADB not available
python3 -c "
import asyncio, sys; sys.path.insert(0, '/home/saber/.hermes/hermes-agent')
from gateway.platforms.weixin import send_weixin_direct
...
asyncio.run(send_apk())
"
```

## Android Permissions (AndroidManifest.xml)

```xml
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.RECORD_AUDIO"/>
<uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS"/>
<uses-permission android:name="android.permission.BLUETOOTH"/>
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT"/>
```

## 方案选择：Flutter App vs 浏览器语音助手

| 场景 | 推荐方案 |
|------|---------|
| 手机/移动端 | Flutter WebRTC（`flutter-webrtc-voice-chatbot`）|
| PC 有物理麦克风 + whisper 可安装 | Python agent.py（端口 8765）|
| PC 无麦克风 / 磁盘满 / whisper 装不了 | **浏览器语音助手**（`pc-voice-agent` skill）|

→ **遇到 ESP32/硬件端语音失败时，优先转向 PC 浏览器方案**，而不是反复调试硬件。

## API Services

| Service | Endpoint | Model |
|---------|----------|-------|
| STT | `POST /v1/audio/speechToText` | speech-01-hd |
| LLM | `POST /v1/text/chatcompletion_v2` | MiniMax-M2.7 |
| TTS | edge-tts (local) | zh-CN-XiaoxiaoNeural |

## Key Insight: Streaming vs Batch

For "normal phone call" latency, everything must stream:
- ❌ Batch: record → stop → send → wait STT → wait LLM → wait TTS → play (5+ second gaps)
- ✅ Streaming: VAD detects speech end → stream STT → stream LLM tokens → stream TTS chunks → play chunks immediately

The bottleneck is TTS latency (3-5 seconds to generate first chunk). Even with streaming, the initial AI response has inherent latency from the model.

## NDK Debugging & WebRTC Android Crash (absorbed from flutter-ndk-debugging + flutter-webrtc-android-crash)

### NDK Build Issues

#### "NDK is not installed" / "[CXX1104] NDK version disagrees"

**Cause**: Flutter SDK hardcodes an NDK version in `FlutterExtension.kt` that doesn't match the installed NDK.

```bash
# Edit Flutter SDK source file
val ndkVersion: String = "28.0.13004108"  # change to working NDK version
```

File: `$FLUTTER_SDK/packages/flutter_tools/gradle/src/main/kotlin/FlutterExtension.kt`

#### NDK 28.2 is broken (clang hangs, missing libs)

**Symptoms**: `clang-19` hangs on any invocation, `ld.lld` missing, `libxml2.so.2` missing.

**Fix**:
```bash
# Symlink lld
ln -s $NDK_PATH/toolchains/llvm/prebuilt/linux-x86_64/bin/ld.lld \
  $NDK_PATH/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android21-clang

# Copy missing libxml2
cp $NDK_PATH/toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/lib/libxml2.so.2 \
  $NDK_PATH/toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/lib/
```

| NDK Version | Status | Notes |
|-------------|--------|-------|
| 28.0.13004108 | ✅ Working | clang-19 works |
| 28.2.13676358 | ❌ Broken | clang hangs |
| 27.0.11902837 | ✅ Works | older but functional |

### WebRTC Runtime Crash (`libjingle_peerconnection_so.so` abort)

**Common crash pattern**: `libjingle_peerconnection_so.so (abort+160)`

**Root causes**: Missing permissions, NDK ABI mismatch, missing STUN servers, wrong flutter_webrtc version.

#### Fix: AndroidManifest.xml

```xml
<uses-permission android:name="android.permission.RECORD_AUDIO"/>
<uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS"/>
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
<uses-permission android:name="android.permission.WAKE_LOCK"/>
<uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
```

#### Fix: build.gradle.kts

```kotlin
defaultConfig {
    minSdk = 24  // WebRTC requires minSdk 24
}
```

#### Fix: pubspec.yaml

```yaml
dependencies:
  flutter_webrtc: ^0.12.12+hotfix.1  # Latest stable
  permission_handler: ^11.3.1
```

#### WebRTC Config (ICE + STUN)

```dart
final Map<String, dynamic> config = {
  'iceServers': [
    {'urls': 'stun:stun.l.google.com:19302'},
    {'urls': 'stun:stun1.l.google.com:19302'},
    {'urls': 'stun:stun2.l.google.com:19302'},
  ],
  'sdpSemantics': 'unified-plan',
  'iceCandidatePoolSize': 10,
};

_pc!.onIceConnectionState = (RTCIceConnectionState state) {
  if (state == RTCIceConnectionState.RTCIceConnectionStateFailed) {
    _pc?.restartIce();
  }
};
```

#### Clean Build

```bash
flutter clean && rm -rf android/.gradle android/build
flutter pub get
flutter build apk --debug
```

#### Known Working Configuration

Tested on: Xiaomi puding (BP2A.250605.031.A3)
- NDK version: `28.0.13004108`
- flutter_webrtc: `0.12.12+hotfix.1`
- minSdk: 24

---

## Files Reference

- `/home/saber/voip-ai-phone/lib/main.dart` - Flutter app source
- `/home/saber/voip-ai-phone/server/server.js` - WebRTC signaling server (port 8080)
- `/home/saber/voip-ai-phone/server/agent.py` - AI streaming server (port 8765)
- `/home/saber/voip-ai-phone/PLAN.md` - Architecture plan
- `$FLUTTER_SDK/packages/flutter_tools/gradle/src/main/kotlin/FlutterExtension.kt` — NDK version default
