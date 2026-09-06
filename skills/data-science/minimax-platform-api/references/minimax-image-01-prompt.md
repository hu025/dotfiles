# MiniMax image-01 生成提示词参考

## 墨琉头像生成（已验证可用）

**生成时间**: 2026-05-12
**API**: `POST https://api.minimaxi.com/v1/image_generation`
**模型**: `image-01`

### Prompt（英文，推荐）
```
A beautiful young woman with long silver-white hair, half tied in a high ponytail with fine silver ribbons and small golden ornaments, naturally curling tips. Pale gray eyes with upward-slanting corners, emitting a faint golden glow, cold and profound gaze. Porcelain-like smooth fair skin, elegant and aloof expression. Wearing silver-white gold-trimmed fitted short combat outfit, holding a small double-snake coiled staff. Fantasy style portrait, cinematic lighting, detailed, ethereal atmosphere.
```

### 中文 Prompt（可用，效果待验证）
```
一个美丽的年轻女性，银白色长发，半扎高马尾，发间点缀细银带和金色小饰品，发尾自然扬起。浅灰色眼眸，眼尾微扬，散发淡金色光芒，冷漠深邃的凝视。瓷白色光滑肌肤，神态优雅冷艳。穿着银白色鎏金收腰短款劲装，手持小巧双蛇缠绕短杖。奇幻风格肖像，电影光效，细节丰富，空灵氛围。
```

### 下载方法（curl -L）
```bash
curl -s -L -o /tmp/avatar.jpeg "https://hailuo-image-algeng-data.oss-cn-wulanchabu.aliyuncs.com/image_inference_output/talkie/prod/img/2026-05-12/xxx.jpeg?Expires=...&OSSAccessKeyId=...&Signature=..."
```

### OSS URL 签名有时效
- `Expires` 字段是 Unix 时间戳，过了就 403
- 签名内嵌在 URL 中，无法自行续期
- 建议生成后立即下载本地保存
