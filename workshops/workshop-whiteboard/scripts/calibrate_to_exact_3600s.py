#!/usr/bin/env python3
"""
Cân chỉnh kịch bản Bản Hợp Đồng 100 Tỷ lên đúng ~9.000 từ để đạt chuẩn 3.600s (60 phút tròn).
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def calibrate():
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    job_file = root_dir / "output" / "jobs" / "job-hop-dong-100-ty-tong-tai.json"
    doc_file = root_dir / "docs" / "kich-ban-tong-tai-1-tieng.md"

    with open(job_file, "r", encoding="utf-8") as f:
        job = json.load(f)

    beats = job["beats"]

    # Bổ sung các đoạn văn miêu tả tâm lý, hình ảnh tinh tế cho từng beat
    additions = {
        5: "\nNgười Kể Chuyện: Không khí trong văn phòng tầng sáu mươi tám như ngưng đọng. Hai thế giới hoàn toàn trái ngược nhau, một bên là quyền lực tối thượng của đế chế Lục Thị, một bên là sự kiên cường trong sạch của Thẩm tiểu thư, chính thức giao nhau tại đây.",
        6: "\nNgười Kể Chuyện: Ánh đèn chùm pha lê rọi xuống những lọn tóc đen mượt của Nhược Hy. Tiếng gót giày của cô vang lên khe khẽ trên sàn đá hoa cương, mở đầu cho một chương đời đầy bí ẩn và thử thách nơi cửa hào môn.",
        8: "\nNgười Kể Chuyện: Lục Cảnh Thâm nắm lấy cổ tay Nhược Hy, hơi ấm từ lòng bàn tay anh truyền qua lớp vải mỏng, như một lời khẳng định ngầm với toàn bộ quan khách rằng người phụ nữ này là giới hạn bất khả xâm phạm.",
        9: "\nNgười Kể Chuyện: Trong đêm tĩnh mịch, ánh trăng bạc chiếu rọi qua khung cửa kính sát đất, kéo dài bóng của hai con người. Căn phòng vốn lạnh lẽo suốt mười năm qua, đêm nay dường như bắt đầu vương vấn một hơi thở dịu êm.",
        11: "\nNgười Kể Chuyện: Trước khi rời khỏi phòng để đến công ty, Cảnh Thâm bước khẽ tới bên cạnh Nhược Hy, nhẹ nhàng kéo chiếc chăn lông cừu đắp lên bờ vai cô, ánh mắt anh dừng lại hồi lâu trên gương mặt thanh tú đang say ngủ.",
        12: "\nNgười Kể Chuyện: Những cuộc gọi khẩn cấp liên tục reo vang trong tổng bộ Lục Thị. Cả thành phố cảng như bao phủ trong một bầu không khí u ám trước ngày mở thầu dự án sống còn mang tầm quốc tế.",
        13: "\nNgười Kể Chuyện: Giữa hai người là một khoảng lặng nghẹt thở. Cảnh Thâm nhìn sâu vào đôi mắt ngấn lệ của Nhược Hy, nơi đáy mắt chỉ có sự tủi hờn trong trẻo chứ tuyệt nhiên không có một tia dối trá nào của kẻ thủ ác.",
        14: "\nNgười Kể Chuyện: Cảnh Thâm siết chặt chiếc điện thoại trong tay, ánh mắt bùng lên ngọn lửa tàn nhẫn của một vị vương giả thương trường. Những kẻ dám mượn tay người phụ nữ của anh để hãm hại Lục Thị sẽ phải trả giá đắt gấp ngàn lần.",
        15: "\nNgười Kể Chuyện: Tiếng ly pha lê chạm nhau lách cách hòa cùng tiếng cười ngạo mạn của Triệu Bích Nguyệt dưới ánh đèn flash của hàng chục phóng viên đang truyền hình trực tiếp đến hàng triệu khán giả trên khắp cả nước.",
        16: "\nNgười Kể Chuyện: Cảnh Thâm ném tập hồ sơ giám định của Cục An ninh xuống bàn chủ tọa, từng trang tài liệu bằng chứng đanh thép bóc trần toàn bộ mạng lưới gián điệp tinh vi của hai kẻ thủ ác trước sự bàng hoàng của cả hội trường.",
        17: "\nNgười Kể Chuyện: Nhược Hy nép sát vào lồng ngực vững chãi của Cảnh Thâm, cảm nhận từng nhịp tim đập mạnh mẽ và ấm áp của anh. Mọi giông bão bên ngoài dường như đều dừng lại sau bờ vai rộng lớn ấy.",
        18: "\nNgười Kể Chuyện: Chiếc hộp gỗ tỏa ra mùi hương trầm cổ kính quyện cùng hương hoa quế thoang thoảng ngoài vườn. Mỗi đường vân cẩn ốc xà cừ đều in hằn dấu vết của thời gian và tấm lòng thương cháu của người bà nhân hậu.",
        19: "\nNgười Kể Chuyện: Gió tuyết mười năm trước dường như lại thổi qua miền ký ức. Giữa lằn ranh sinh tử nơi vực sâu lạnh buốt, một cô bé quàng khăn len đỏ đã trở thành đức tin và lẽ sống duy nhất để cậu thiếu niên họ Lục kiên cường bước tiếp.",
        20: "\nNgười Kể Chuyện: Nhược Hy áp chiếc khăn len sờn rách vào ngực, nơi trái tim đang đập rộn ràng từng hồi. Tình yêu sâu kín và sự hy sinh thầm lặng của người đàn ông ấy đã làm tan chảy mọi rào cản phòng ngự trong tâm hồn cô.",
        21: "\nNgười Kể Chuyện: Từng góc nhỏ trong căn biệt thự Ngự Cảnh Uyển đều in đậm bóng hình và tiếng cười của hai người suốt một năm qua. Nhược Hy khẽ chạm tay lên chiếc bàn trà, khóe mắt vương một giọt lệ lặng lẽ rơi xuống sàn.",
        22: "\nNgười Kể Chuyện: Cảnh Thâm đứng chôn chân trong bóng tối, khao khát muốn bước tới ôm chầm lấy cô từ phía sau nhưng lòng tự tôn và nỗi sợ bị cô cự tuyệt đã ghì chặt đôi chân của người đàn ông quyền lực.",
        23: "\nNgười Kể Chuyện: Tiếng kim đồng hồ tích tắc gõ nhịp trong màn đêm hoang vắng. Ngôi biệt thự rộng lớn bỗng chốc trở nên thênh thang và lạnh lẽo đến rợn người khi thiếu vắng bóng dáng nhỏ bé của người con gái ấy.",
        26: "\nNgười Kể Chuyện: Ánh hoàng hôn rực rỡ buông xuống phi trường quốc tế, nhuộm vàng đôi uyên ương đang ôm chặt lấy nhau giữa muôn ngàn tràng pháo tay chúc phúc. Một cái kết trọn vẹn và viên mãn nhất cho câu chuyện tình yêu mười năm đầy định mệnh."
    }

    for b_idx, add_text in additions.items():
        if b_idx < len(beats):
            beats[b_idx]["rawText"] += add_text

    total_words = sum(len(b["rawText"].split()) for b in beats)
    print(f"[*] Tổng số từ sau khi cân chỉnh: {total_words} từ")

    job["beats"] = beats
    with open(job_file, "w", encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False, indent=2)

    print(f"[OK] Đã cập nhật file: {job_file}")

if __name__ == "__main__":
    calibrate()
