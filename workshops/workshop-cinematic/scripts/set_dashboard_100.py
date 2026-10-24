import requests

payload = {
    'progress': 100,
    'step_id': 'completed',
    'step_detail': 'Hoàn tất Master Film 104 phân cảnh AI Veo 2 (GEN V) cho kênh Giải Mã Tech!',
    'log_line': '🎉 104/104 video AI hoàn thành. Phim Full HD 1080p xuất xưởng tại output/cinematic/job-ai-agent-giaimatech-10min.mp4'
}
try:
    r = requests.post('http://127.0.0.1:8100/api/studio/progress/job-ai-agent-giaimatech-10min/update', json=payload, timeout=3)
    print('Dashboard progress set to 100%:', r.status_code)
except Exception as e:
    print('Dashboard err:', e)
