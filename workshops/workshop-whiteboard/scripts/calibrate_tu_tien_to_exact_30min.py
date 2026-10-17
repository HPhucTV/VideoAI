#!/usr/bin/env python3
"""
Cân chỉnh kịch bản PHẾ ĐAN NGHỊCH THIÊN (TRO TÀN ĐỊA HỎA)
đạt đúng mốc 30 phút (1.800 giây = 30.0 phút) theo đúng tỷ lệ từng hồi và phân cảnh.
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def calibrate():
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    job_file = root_dir / "output" / "jobs" / "job-phe-dan-nghich-thien.json"

    with open(job_file, "r", encoding="utf-8") as f:
        job = json.load(f)

    beats = job["beats"]

    # Mapping beat index -> extra narrative prose
    additions = {
        # SCENE 02 (Beats 3, 4, 5) -> target +45s (~140 words)
        3: "\nNgười Kể Chuyện: Từng mảng xỉ đen rơi xuống sàn đá nóng bỏng, phát ra những tiếng xèo xèo ghê rợn. Hơi nóng và độc khí bốc lên nghi ngút như muốn thiêu rụi lông mi của cậu. Nhưng đôi mắt Lâm Mặc vẫn mở trừng trừng trong làn khói đen kịt, cẩn thận quan sát từng đường rãnh kim loại bên trong lòng lò.",
        4: "\nTiểu Thạch Đầu: 'Nhà đệ nghèo lắm, cha mẹ mất sớm trong đợt yêu thú tràn qua làng. Đệ cứ nghĩ vào được Thanh Vân Tông làm tạp dịch là có ngày đổi đời, gửi được bạc về nuôi em gái nhỏ... Nào ngờ ở đây mạng người còn rẻ hơn củi đốt lò. Mặc ca, huynh là người duy nhất coi đệ là con người...'\nNgười Kể Chuyện: Lâm Mặc nhìn khuôn mặt non nớt lấm lem muội than của cậu bé, khẽ thở dài một tiếng, ánh mắt thoáng hiện một tia ấm áp hiếm hoi giữa chốn địa ngục tàn khốc.",
        5: "\nNgười Kể Chuyện: Độc tố của vạn viên phế đan cổ xưa tích tụ mười năm, kẻ khác chạm vào ắt nát da rữa thịt. Nhưng dưới sự vận chuyển kỳ diệu của Phệ Độc Chuyển Nguyên Quyết, kịch độc chuyển hóa thành một dòng nhiệt lưu ấm áp rót thẳng vào đan điền, tôi luyện xương tủy cậu cứng cáp như huyền thiết.",

        # SCENE 03 (Beats 6, 7, 8) -> target +45s (~140 words)
        6: "\nNgười Kể Chuyện: Khí thế của thiên tài Trúc Cơ Hậu Kỳ tỏa ra ngùn ngụt như núi cao sừng sững, đè ép không gian xung quanh vặn vẹo. Đám tạp dịch khốn khổ nằm bẹp dưới đất, lồng ngực bị ép nghẹt đến mức không thở nổi, có kẻ yếu ớt đã bắt đầu nôn ra từng ngụm máu bầm.",
        7: "\nNgười Kể Chuyện: Cú va đập mạnh khiến Tiểu Thạch Đầu hoa mắt chóng mặt, khóe miệng rỉ máu tươi. Nhưng cậu bé không dám kêu một tiếng, chỉ biết ôm đầu run rẩy nép sát vào gờ đá lạnh, sợ hãi trước ánh mắt khinh miệt lạnh lùng như băng của vị thiên tài kiêu ngạo.",
        8: "\nTriệu Vô Cực: 'Chỉ cần viên đan dược thượng phẩm này xuất thế, không những Sở sư điệt có thể thuận lợi ngưng kết Kim Đan cửu phẩm vô hà, mà lão phu cũng có thể mượn dược lực dư thừa để đột phá bình cảnh trăm năm! Cả ngọn Địa Hỏa Phong này, tất cả đều được vận hành để phục vụ cho sự nghiệp huy hoàng của chúng ta!'",

        # SCENE 04 (Beats 9, 10, 11) -> target +64s (~200 words)
        9: "\nNgười Kể Chuyện: Lâm Mặc lén nhìn theo những rãnh hoa văn uốn lượn chạy khắp mặt sàn, trong lòng dâng lên một luồng ớn lạnh thấu xương. Đây tuyệt đối không phải trận pháp tụ hỏa luyện đan thông thường của chính đạo danh môn, mà là một nhánh tà trận cổ xưa chuyên dùng để rút cạn nguyên thần và khí huyết của sinh linh làm chất xúc tác.",
        10: "\nNgười Kể Chuyện: 'Uống đi! Uống hết vào! Đây là ân huệ ngập tràn của thiên tài tông môn ban tặng, kẻ nào không uống chính là bất kính với bề trên!' Tiếng quát tháo của đám giám sự tay cầm roi da vang dội khắp bốn phía, ép buộc những bàn tay run rẩy phải vội vã đưa viên đan độc màu đỏ máu vào miệng nuốt chửng.",
        11: "\nLâm Mặc: 'Ba năm qua, ta đã âm thầm dùng thanh đoản đao cùn này đào thủng một đường hầm nhỏ thông xuống mạch dung nham ngầm bên dưới Lò Số Chín. Chỉ cần đến giờ Tý khi trận pháp chưa kịp hoàn toàn khép kín, ta sẽ đưa đệ thoát khỏi nơi này, rời xa Thanh Vân Tông vĩnh viễn.'\nTiểu Thạch Đầu gật đầu lia lịa, hai mắt ngấn lệ nhìn người huynh trưởng đáng tin cậy duy nhất của mình.",

        # SCENE 05 (Beats 12, 13, 14) -> target +94s (~290 words)
        12: "\nNgười Kể Chuyện: Ánh trăng Huyết Nguyệt chiếu rọi qua giếng trời tròn xoe, tựa như một con mắt đỏ ngầu khổng lồ của hung thần thượng cổ đang mở to nhìn trừng trừng xuống đáy vực thẳm. Sức ép từ trận pháp Kim Đan khiến không khí trở nên đặc quánh như vũng bùn lầy, mỗi một hơi thở đều nặng nhọc và buốt rát như nuốt phải mảnh thủy tinh vụn.",
        13: "\nNgười Kể Chuyện: 'Cứu con với! Mẹ ơi... cứu con!' Tiếng gào khóc ai oán vang vọng khắp đại điện tối tăm. Những cơ thể từng là thanh niên trai tráng giờ đây co rúm lại như những cành củi khô mục nát dưới nắng hè gay gắt. Từng sợi tơ máu li ti đỏ rực bị hút ra từ lỗ chân lông, xoáy tròn thành những dải lụa huyết sắc bay lượn trên không trung rồi bị nuốt chửng vào chín miệng rồng thao thiết bằng đồng.",
        14: "\nNgười Kể Chuyện: Sở Thiên Kiêu khẽ lắc nhẹ chén trà ngọc bích, nhìn ngắm những dải sương máu cuồn cuộn bay vào lò đan với vẻ mặt thưởng thức như đang chiêm ngưỡng một bức tranh thủy mặc tuyệt tác. Đối với một thiên tài đỉnh phong đứng trên đỉnh cao quyền lực, mạng sống của hàng trăm tạp dịch chỉ là những viên sỏi lót đường cho con đường trường sinh bất tử của hắn mà thôi.",

        # SCENE 06 (Beats 15, 16, 17) -> target +70s (~220 words)
        15: "\nNgười Kể Chuyện: 'Đứng lại! Đám sâu bọ kia, đại trận huyết tế đang vận hành, ai cho phép các ngươi lén lút trốn chạy?!' Hai tên chấp sự gầm lên dữ tợn, linh lực Trúc Cơ Sơ Kỳ bùng phát cuốn theo gió lốc bụi than mù mịt, phong tỏa hoàn toàn lối đi hẹp dẫn về phía sau Lò Số Chín.",
        16: "\nNgười Kể Chuyện: Thanh phi kiếm lạnh buốt găm sâu vào da thịt non nớt. Thân hình nhỏ nhắn của Tiểu Thạch Đầu mềm nhũn ra, gục đầu vào vai Lâm Mặc. Máu từ miệng cậu bé trào ra ướt đẫm cả lồng ngực gầy guộc. Cậu dùng chút tàn lực cuối cùng siết chặt lấy bàn tay Lâm Mặc, khóe môi khẽ mỉm cười thanh thản vì đã cứu được người huynh trưởng thân yêu nhất trần đời.",
        17: "\nNgười Kể Chuyện: Nhìn đứa em nhỏ trút hơi thở cuối cùng trong lòng mình, một sợi dây xích vô hình trói buộc tâm cảnh của Lâm Mặc suốt mười năm qua bỗng chốc đứt phăng! Đôi mắt cậu đỏ ngầu rực lửa hận thù, sát khí đậm đặc ngưng tụ thành thực chất khiến nhiệt độ xung quanh lò đan hạ xuống điểm đóng băng. Cậu bóp nát thanh phi kiếm thép trong sự ngỡ ngàng tột độ của kẻ địch.",

        # SCENE 07 (Beats 18, 19, 20) -> target +97s (~300 words)
        18: "\nNgười Kể Chuyện: Vạn đạo vân độc tử kim trên cơ thể Lâm Mặc bừng sáng chói lọi, chiếu rọi cả góc tối đại điện. Khí tức Trúc Cơ Đại Viên Mãn bộc phát làm cuốn tung toàn bộ muội than và xỉ đan dưới đất bay lên trời như một trận bão đen. Hai tên chấp sự đứng đối diện bị áp lực linh hồn nghiền nát, cả người run rẩy không sao nhấc nổi một ngón tay trước khi bị ngọn lửa đen nuốt chửng hoàn toàn.",
        19: "\nNgười Kể Chuyện: 'ẦM ẦM ẦM!' Tiếng va chạm giữa Phệ Độc Chưởng và chín đạo kiếm ảnh vang lên như tiếng sét đánh ngang tai. Ngọn lửa độc đen tuyền bùng lên ngùn ngụt, nuốt chửng toàn bộ kiếm khí sắc bén của môn phái chính đạo. Linh bảo thượng phẩm mà phụ thân Sở Thiên Kiêu ban tặng bắt đầu nứt toác từng vết rạn, linh quang hộ thể bị ăn mòn rỉ sét trong chớp mắt, biến thành những mảnh sắt vụn rơi rụng lả tả.",
        20: "\nNgười Kể Chuyện: 'Không! Cha ta sẽ giết ngươi... Cả nhà ngươi sẽ chết không có chỗ chôn...' Sở Thiên Kiêu giãy giụa tuyệt vọng trong bàn tay thép của Lâm Mặc, hai chân đạp loạn xạ giữa không trung. Nhưng câu trả lời đáp lại hắn chỉ là ánh mắt lạnh lùng như nhìn một xác chết của Lâm Mặc, cùng cú ném dứt khoát đẩy thẳng hắn vào lòng chảo lửa đỏ rực của Cửu Long Lô.",

        # SCENE 08 (Beats 21, 22, 23) -> target +104s (~320 words)
        21: "\nNgười Kể Chuyện: Tiếng gầm của Triệu Vô Cực làm rung chuyển cả ngọn núi Địa Hỏa. Cột đá khổng lồ dày cả trượng nứt toác đổ sụp xuống, đất đá rơi rào rào như mưa. Uy áp của một vị tu sĩ Kim Đan chân chính đè nặng lên từng tấc da thịt Lâm Mặc, khiến máu tươi từ các vết nứt trên người cậu bắn ra thành từng tia đỏ thẫm.",
        22: "\nNgười Kể Chuyện: 'Ngươi nghĩ ta cạo xỉ mười năm chỉ là làm việc nô dịch vô nghĩa sao?' Lâm Mặc cười vang giữa sấm sét. Máu độc của cậu ngấm sâu vào từng mạch trận cổ xưa dưới đáy chín mươi chín lò phụ, biến toàn bộ trận pháp điều khiển địa hỏa của Triệu Vô Cực thành một cạm bẫy phản phệ kinh thiên động địa! Chín con rồng lửa gầm rú xé rách màng nhĩ, hung hãn quay ngoắt đầu lại lao vào xé nát lớp linh thuẫn của chính chủ nhân.",
        23: "\nNgười Kể Chuyện: Thanh Cự Kiếm mười trượng ngưng tụ toàn bộ hận thù và độc tính mười năm rạch một đường đen ngòm giữa hư không, chém thẳng xuống đỉnh đầu Triệu Vô Cực. Không gian như vỡ vụn trước nhát chém long trời lở đất. Tiếng nổ đanh gọn vang lên khi viên Kim Đan hai trăm năm của lão trưởng lão bị bổ đôi, thiêu đốt toàn bộ sinh lực của lão thành một bãi tro tàn đen ngòm.",

        # SCENE 09 (Beats 24, 25, 26) -> target +35s (~110 words)
        24: "\nNgười Kể Chuyện: Mùi hương kỳ dị lan tỏa khắp đại điện, làm dịu đi mùi máu tanh nồng nặc. Viên đan dược xoay tròn chậm rãi giữa không trung, hấp thụ toàn bộ tinh hoa linh khí còn sót lại của đất trời.",
        25: "\nNgười Kể Chuyện: Dược lực cuồng bạo nóng như nham thạch chảy dọc theo kinh mạch, gột rửa toàn bộ tạp chất trong cơ thể cậu, tôi luyện đan điền thành một hồ chứa linh lực tử kim sắc rực rỡ vô biên.",
        26: "\nNgười Kể Chuyện: Cột sáng tím vàng xuyên thẳng qua tầng mây trên đỉnh núi cao, báo hiệu cho toàn thể tu chân giới biết rằng một con quái vật sinh ra từ tro tàn và kịch độc đã chính thức thức tỉnh.",

        # SCENE 10 (Beats 27, 28, 29) -> target +10s (~30 words)
        27: "\nNgười Kể Chuyện: Từng bước chân của Lâm Mặc đạp lên hư không vững chãi như dẫm lên bậc thang vô hình, dáng dấp kiêu hãnh bất khuất giữa hàng ngàn mũi kiếm đang nhắm vào mình.",
        28: "\nNgười Kể Chuyện: Mảnh lệnh bài Chưởng tọa rơi tòm xuống vực sâu dung nham, tan biến vĩnh viễn như lời đoạn tuyệt dứt khoát với mười năm làm nô dịch tủi nhục.",
        29: "\nNgười Kể Chuyện: Ánh sáng bình minh rực rỡ soi sáng con đường thênh thang phía trước, mở ra một trang sử mới đầy kiêu hùng cho kẻ nghịch thiên đoạt mệnh."
    }

    for b_idx, add_text in additions.items():
        if b_idx < len(beats):
            beats[b_idx]["rawText"] += add_text

    total_words = sum(len(b["rawText"].split()) for b in beats)
    print(f"[*] Tong so tu sau khi can chinh: {total_words} tu")

    job["beats"] = beats
    with open(job_file, "w", encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False, indent=2)

    print(f"[OK] Da cap nhat file: {job_file}")

if __name__ == "__main__":
    calibrate()
