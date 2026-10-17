#!/usr/bin/env python3
"""
OmniVideo Studio - Workshop 3 (Whiteboard)
Tạo Job JSON chuẩn 30 Phút (~4.700 - 4.800 từ) cho kịch bản điện ảnh Tu Tiên:
PHẾ ĐAN NGHỊCH THIÊN (TRO TÀN ĐỊA HỎA)
Đạt đúng mốc 30 phút trọn vẹn (1800 giây) theo đúng 5 Hồi và 10 Cảnh.
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def build_job():
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    job_output = root_dir / "output" / "jobs" / "job-phe-dan-nghich-thien.json"
    job_output.parent.mkdir(parents=True, exist_ok=True)

    chapters = [
        # =========================================================================
        # HỒI 1: TRO TÀN DƯỚI ĐÁY LÒ ĐAN (Phút 00:00 – 04:30)
        # =========================================================================
        (
            "HỒI I - CẢNH 1: ĐẠI CẢNH THANH VÂN TÔNG & ĐỊA HỎA PHONG",
            "scene-01",
            [
                (
                    "Đỉnh Thanh Vân Tráng Lệ",
                    "Tiên giới rực rỡ và kiếm quang vạn trượng",
                    "Thanh Vân Tông ngút ngàn mây phủ và hạc trắng bay lượn",
                    "scene", 100,
                    """Người Kể Chuyện: Người đời ngước nhìn Thanh Vân Tông, chỉ thấy tiên sơn vạn trượng, ngút ngàn mây trắng lượn quanh những cung điện nguy nga tráng lệ. Từng đàn hạc trắng xòe cánh lướt qua rặng tùng ngàn năm, những đệ tử nội môn khoác trường bào trắng muốt phiêu dật, ngự kiếm phi hành rạch ngang bầu trời xanh thẳm như những vệt sao băng. Nơi đây là thánh địa tu tiên mà hàng ức phàm nhân trong thiên hạ quỳ lạy, khát khao được một lần chạm tay tới ngưỡng cửa trường sinh bất lão, vứt bỏ hồng trần ô trọc."""
                ),
                (
                    "Vực Thẳm Địa Hỏa Ngàn Trượng",
                    "Máy quay xuyên qua ngàn trượng đá đen đặc",
                    "Vực sâu Địa Hỏa Đan Phòng rực dung nham và khói độc",
                    "scene", 680,
                    """Người Kể Chuyện: Nhưng không ai biết rằng, ngay dưới chân ngọn tiên sơn vạn kiếp thanh tịnh ấy, máy quay đâm chúc thẳng xuống lòng đất, xuyên qua hàng ngàn trượng đá đen đặc quánh. Nơi đây là Địa Hỏa Đan Phòng, nơi tăm tối và ngột ngạt nhất của Thanh Vân Tông. Không có ánh mặt trời, chỉ có những dòng sông dung nham đỏ rực sùng sục chảy qua các khe nứt, khói độc màu lục bốc lên nghi ngút làm mù mắt người, cùng mùi lưu huỳnh nồng nặc và những tiếng ho sù sụ của những kẻ đang hấp hối."""
                ),
                (
                    "Mồ Chôn Những Kẻ Phế Vật",
                    "Máu thịt đốt lò nuôi dưỡng tiên môn",
                    "Hàng trăm tạp dịch cùm xích gầy trơ xương bên lò đan",
                    "character", 1260,
                    """Người Kể Chuyện: Để nâng đỡ đám tiên nhân áo trắng không vướng bụi trần trên chín tầng mây kia, dưới đáy Địa Hỏa Phong sâu ngàn trượng, có hàng trăm kẻ phế vật ngoại môn đang phải dùng chính máu thịt và sinh mệnh của mình để ngày đêm đốt lò, cạo xỉ, chịu đựng đan độc gặm nhấm từng tấc kinh mạch. Giới tu tiên tàn khốc lấy sức mạnh làm tôn chỉ. Kẻ không có linh căn thượng phẩm, ở nơi này mạng sống còn rẻ rúng hơn cỏ rác ven đường."""
                )
            ]
        ),
        (
            "HỒI I - CẢNH 2: BÊN TRONG LÒ ĐAN SỐ 9",
            "scene-02",
            [
                (
                    "Cạo Xỉ Đan Trong Lò Nóng",
                    "Lâm Mặc và đôi tay nổi gân độc tím đen",
                    "Lâm Mặc mặc áo thô rách cạo xỉ đan trong lòng đỉnh đồng",
                    "character", 100,
                    """Người Kể Chuyện: Bên trong Lò Đan Số Chín, cái nóng như thiêu như đốt bốc lên từ thành đỉnh đồng khổng lồ nặng cả vạn cân. Lâm Mặc, thiếu niên hai mươi tuổi, khoác trên mình manh áo vải thô rách bươm lem luốc muội than đen kịt. Cậu chui hẳn người vào bụng lò còn hầm hập lửa đỏ, bàn tay gầy gò cầm một thanh đoản đao cùn gỉ sét, cặm cụi cạo từng mảng xỉ đan đen sì bám chặt vào kim loại. Dưới làn da tái nhợt của cậu, những đường gân màu tím đen chằng chịt nổi lên như rễ cây cổ thụ, dấu hiệu của mười năm đan độc tích tụ đã ngấm sâu vào tủy sống."""
                ),
                (
                    "Bát Nước Đục Của Tiểu Thạch Đầu",
                    "Mạng người tạp dịch như bao tải rách",
                    "Tiểu Thạch Đầu bưng bát nước run rẩy trước cửa lò",
                    "scene", 680,
                    """Người Kể Chuyện: Phía ngoài cửa lò, hai tên giám sự vừa lạnh lùng lôi đi một cái xác khô quắt của một đệ tử tạp dịch lò số bốn, quẳng lên xe kéo như vứt bỏ một bao tải rác mục. Tiểu Thạch Đầu, cậu bé mười lăm tuổi mới vào đan phòng, hai chân run lẩy bẩy, hai tay bưng bát nước đục ngầu hớt hải chạy tới trước cửa Lò Số Chín.
Tiểu Thạch Đầu: "Mặc ca... Lò số bốn lại có người chết rồi! Huynh mau ra ngoài nghỉ một lát đi! Thành lò còn nóng rực thế kia, đan độc bốc lên sẽ ngấm thẳng vào tim mất!"
Lâm Mặc: "Xỉ đan không cạo sạch lúc lò còn nóng đỏ, đợi nguội đi sẽ cứng như huyền thiết ngàn năm. Đến lúc đó không hoàn thành chỉ tiêu, roi da của giám sự quất xuống lưng... còn đau buốt hơn đan độc gấp mười lần." """
                ),
                (
                    "Bí Mật Phệ Độc Chuyển Nguyên Quyết",
                    "Mười năm nuốt độc cầu một con đường sống",
                    "Viên phế đan tan biến vào lòng bàn tay Lâm Mặc",
                    "concept", 1260,
                    """Người Kể Chuyện: Đợi Tiểu Thạch Đầu quay lưng đi, Lâm Mặc lặng lẽ khép hờ cửa lò. Trong bóng tối đặc quánh, khóe môi cậu rỉ ra một vệt máu đen sẫm, nhưng ánh mắt cậu lại tĩnh lặng sâu thẳm như mặt hồ đóng băng ngàn năm. Cậu siết chặt viên xỉ đan độc đặc quánh trong lòng bàn tay. Một luồng hắc khí tử độc cuồn cuộn bị vết sẹo giữa lòng bàn tay cậu hút cạn vào trong da thịt. Những đường gân tím trên cánh tay bỗng lóe lên ánh vàng kim rực rỡ rồi nhanh chóng thu liễm lại.
Lâm Mặc: "Mười năm ròng rã. Ba ngàn sáu trăm năm mươi ngày nuốt phế đan, uống độc hỏa vào người. Người đời luyện đan cầu trường sinh phi thăng... Còn Lâm Mặc ta luyện độc, chỉ cầu gom đủ sức mạnh để có một ngày toàn mạng bước ra khỏi cái địa ngục này!" """
                )
            ]
        ),

        # =========================================================================
        # HỒI 2: MÙI MÁU TRONG ĐAN HƯƠNG (Phút 04:30 – 10:30)
        # =========================================================================
        (
            "HỒI II - CẢNH 3: THIÊN TÀI GIÁNG LÂM",
            "scene-03",
            [
                (
                    "Kiếm Khí Giáng Lâm",
                    "Cửa đá mở toang và sự kiêu ngạo của chân truyền",
                    "Sở Thiên Kiêu chân không chạm đất bước vào đại điện",
                    "character", 100,
                    """Người Kể Chuyện: RẦM! Cánh cửa đá nặng vạn cân ngăn cách Địa Hỏa Đan Phòng với thế giới bên ngoài đột ngột mở toang. Một luồng kiếm khí buốt giá thấu xương tràn vào như thác lũ, quét sạch toàn bộ khói độc màu lục dạt sang hai bên vách đá. Giữa làn kiếm quang rực rỡ, Sở Thiên Kiêu ung dung bước vào. Hắn mặc trường bào gấm trắng thêu chỉ vàng lộng lẫy, chân không hề chạm đất nửa tấc, xung quanh toàn thân bao bọc một màn linh quang hộ thể màu xanh ngọc bích trong vắt, ngăn cách hoàn toàn với bụi than nhơ bẩn của đan phòng.
Tiếng chuông đồng ngân vang từng hồi dồn dập, hàng trăm tạp dịch đệ tử run rẩy quỳ rạp rạp xuống nền đá nóng rực, không một ai dám ngẩng đầu nhìn thẳng."""
                ),
                (
                    "Sự Tàn Bạo Của Kẻ Bề Trên",
                    "Tiểu Thạch Đầu bị hất văng vào vách đá",
                    "Sở Thiên Kiêu phất tay áo tạo cuồng phong băng giá",
                    "action", 680,
                    """Người Kể Chuyện: Đi cạnh vị thiên tài hai mươi hai tuổi đạt cảnh giới Trúc Cơ Hậu Kỳ là Triệu Vô Cực, Chưởng tọa Địa Hỏa Đan Phòng với nụ cười nịnh nọt lấy lòng. Nhìn thấy Tiểu Thạch Đầu đang ngơ ngác đứng bên lối đi, Sở Thiên Kiêu cau mày ghê tởm, vung nhẹ ống tay áo tạo nên một trận cuồng phong linh lực sắc lẹm, hất văng cậu bé mười lăm tuổi bay thẳng vào vách đá sắc nhọn.
Sở Thiên Kiêu: "Đám kiến hôi Luyện Khí kỳ bẩn thỉu này thở ra toàn mùi hôi thối của phế đan, làm bẩn cả linh y của ta! Triệu trưởng lão, ông có chắc chắn Cửu Long Huyết Lô ở đây gom đủ hỏa hầu để luyện viên Cửu Chuyển Phá Cảnh Đan cho bản công tử đột phá Kim Đan chứ?" """
                ),
                (
                    "Ánh Mắt Đồ Tể Của Triệu Vô Cực",
                    "Nguyên liệu phụ trợ nuôi dưỡng suốt ba năm",
                    "Triệu Vô Cực nhìn đám tạp dịch như bầy gia súc chờ mổ thịt",
                    "character", 1260,
                    """Người Kể Chuyện: Triệu Vô Cực khẽ khom lưng, nụ cười giả tạo trên khuôn mặt già nua nhăn nheo càng thêm phần quỷ quyệt, độc địa. Lão đưa bàn tay gầy guộc vuốt chòm râu dê, ánh mắt đảo qua hàng trăm thân ảnh tạp dịch đang run rẩy quỳ dưới sàn đất.
Triệu Vô Cực: "Sở sư điệt cứ việc yên tâm! Lò Cửu Long này thông thẳng với mạch Địa Tâm Hỏa sâu nhất. Hơn nữa... toàn bộ dược liệu quý hiếm và nguồn nguyên liệu phụ trợ đặc biệt mà lão phu dày công chuẩn bị suốt ba năm qua, đêm nay đã hoàn toàn chín muồi. Chỉ cần ngọn lửa bùng lên, Kim Đan của công tử chắc chắn sẽ viên mãn thành hình!"
Người Kể Chuyện: Ánh mắt của Triệu Vô Cực lúc này không phải nhìn những con người bằng xương bằng thịt, mà như một gã đồ tể đang thèm thuồng nhìn bầy gia súc béo tốt chờ ngày đưa lên bàn mổ."""
                )
            ]
        ),
        (
            "HỒI II - CẢNH 4: PHÁT HIỆN BẤT THƯỜNG",
            "scene-04",
            [
                (
                    "Rãnh Đá Hút Cạn Giọt Máu",
                    "Lâm Mặc phát hiện trận văn quái dị dưới sàn",
                    "Vết máu trên rãnh đá phát ra tia sáng đỏ như máu",
                    "concept", 100,
                    """Người Kể Chuyện: Khi đám người quyền quý vừa bước lên đài cao, Lâm Mặc nhanh chóng bò tới góc vách đá, đỡ Tiểu Thạch Đầu đang rên rỉ đứng dậy. Khóe trán cậu bé bị rách một mảng lớn, máu tươi nhỏ từng giọt xuống khe nứt của sàn đá. Bất chợt, đồng tử Lâm Mặc co rút kịch liệt. Giọt máu tươi rơi xuống khe đá khắc hoa văn cổ xưa, thay vì bị sức nóng ngàn độ của địa hỏa bốc hơi, lại bị những rãnh trận pháp hút cạn sạch trong chớp mắt! Ngay sau đó, một tia sáng màu đỏ thẫm quái dị như mạch máu người khẽ chớp lên rồi lặn sâu vào lòng đất."""
                ),
                (
                    "Bẫy Linh Đan Màu Đỏ Thẫm",
                    "Viên Tịch Cốc Đan ban thưởng của Sở công tử",
                    "Triệu Vô Cực ra lệnh phát đan dược cho toàn bộ tạp dịch",
                    "scene", 680,
                    """Người Kể Chuyện: Ngay lúc đó, tiếng Triệu Vô Cực từ trên đài cao vang vọng xuống, kèm theo lệnh phong tỏa toàn bộ các cửa thông gió của đan phòng. Các giám sự cầm những khay đồng chứa đầy những viên đan dược màu đỏ sẫm tỏa ra mùi thơm ngào ngạt khác thường, phân phát cho từng đệ tử tạp dịch, tuyên bố đây là linh đan bồi dưỡng đặc biệt do Sở công tử hào phóng ban phát trước đêm đại luyện đan. Đám tạp dịch khốn khổ vì đói khát và kiệt sức mừng rỡ như bắt được vàng, thi nhau nuốt ực vào bụng mà không chút mảy may nghi ngờ."""
                ),
                (
                    "Âm Mưu Huyết Dẫn Đêm Huyết Nguyệt",
                    "Chín mươi chín sinh mạng làm thuốc dẫn tế lô",
                    "Lâm Mặc bóp chặt cổ tay hất văng viên đan độc",
                    "character", 1260,
                    """Người Kể Chuyện: Tiểu Thạch Đầu vừa run rẩy cầm viên đan định bỏ vào miệng thì một bàn tay thô ráp như kìm sắt bất ngờ bóp chặt cổ tay cậu bé, hất văng viên linh đan vào góc tối lò đan.
Tiểu Thạch Đầu: "Mặc ca... đó là linh đan ban thưởng của chân truyền sư huynh mà..."
Lâm Mặc: "Đó không phải Tịch Cốc Đan! Trong viên đan đó chứa Huyết Dẫn Thảo ngàn năm và Tỏa Linh Tán cực độc! Uống vào, toàn bộ kinh mạch và đan điền sẽ bị khóa chặt, còn khí huyết toàn thân sẽ sôi trào hóa thành linh dịch tinh khiết nhất. Đêm nay là đêm Huyết Nguyệt trăm năm xuất hiện một lần... Lão già độc ác đó không hề dùng thảo dược để luyện đan. Lão muốn dùng sinh mạng của chín mươi chín con người trong căn phòng này làm thuốc dẫn tế lò!" """
                )
            ]
        ),

        # =========================================================================
        # HỒI 3: HUYẾT NGUYỆT TẾ LÔ (Phút 10:30 – 17:30)
        # =========================================================================
        (
            "HỒI III - CẢNH 5: ĐẠI TRẬN KHỞI ĐỘNG",
            "scene-05",
            [
                (
                    "Huyết Nguyệt Giờ Tý",
                    "Tám tầng phù lục phong ấn lối thoát duy nhất",
                    "Ánh trăng máu chiếu thẳng xuống đỉnh Cửu Long Huyết Lô",
                    "scene", 100,
                    """Người Kể Chuyện: Đúng giờ Tý, bóng đêm ngoài kia chuyển sang một màu đỏ rực ma quái. Từ giếng trời khổng lồ thông thẳng lên đỉnh núi lửa, một luồng ánh sáng huyết nguyệt đỏ như máu tươi chiếu thẳng xuống đỉnh Cửu Long Lô đặt sừng sững giữa trung tâm đại điện. Trên đài cao, Triệu Vô Cực nở nụ cười dữ tợn, hai tay bắt pháp quyết phức tạp. ẦM ẦM! Tám lá phù lục Kim Đan bay vút ra, dán chặt lên cánh cửa đá duy nhất của Địa Hỏa Phòng, hoàn toàn phong tỏa mọi đường sống. Toàn bộ sàn đá dưới chân bừng sáng rực rỡ những đường vân trận pháp đỏ ngầu như một biển máu cuộn trào."""
                ),
                (
                    "Bi Kịch Khô Quắt Thành Huyết Vụ",
                    "Chín đầu rồng gầm rú nuốt trọn tinh huyết tạp dịch",
                    "Các tạp dịch gào thét quằn quại cơ thể teo tóp lại",
                    "action", 680,
                    """Người Kể Chuyện: Chín đầu rồng bằng đồng cổ xưa trên thân lò đan bất chợt phát ra những tiếng gầm rú xé rách màng nhĩ. Đan độc bên trong cơ thể những tạp dịch đã nuốt viên đan lúc chiều phát tác dữ dội. Họ ngã lăn ra đất, ôm ngực quằn quại gào thét trong đau đớn cùng cực. Da thịt họ khô quắt lại với tốc độ mắt thường cũng có thể nhìn thấy, từng dòng tinh huyết đỏ thắm bốc hơi thành những dải sương máu cuồn cuộn bay thẳng lên không trung, bị chín miệng rồng hút trọn vào bụng lò.
Tạp Dịch: "Trưởng lão! Ngài đã hứa chỉ cần chúng con canh lửa hết năm nay sẽ cho vào ngoại môn mà! Tại sao... tại sao lại giết chúng con tàn nhẫn như vậy?!" """
                ),
                (
                    "Sự Tàn Nhẫn Của Chính Đạo",
                    "Sở Thiên Kiêu ung dung nhấp chén trà ngon",
                    "Sở Thiên Kiêu ngồi xếp bằng coi mạng người như cỏ rác",
                    "character", 1260,
                    """Người Kể Chuyện: Trước cảnh tượng địa ngục trần gian đầy máu và tiếng la khóc xé lòng, Sở Thiên Kiêu ngồi xếp bằng trên đài cao vẫn bình thản nâng chén trà linh dược lên nhấp từng ngụm nhỏ, phong thái thanh tao thoát tục nhưng lời thốt ra lại lạnh lùng tàn nhẫn đến thấu xương.
Sở Thiên Kiêu: "Thiên tư hạ đẳng ngu dốt, cả đời các ngươi cũng không thể vượt qua nổi Luyện Khí tầng bốn. Dù có sống thêm vài chục năm nữa thì cũng chỉ làm lãng phí linh khí của trời đất Thanh Vân. Hôm nay được hóa thành một phần tinh huyết trong viên Kim Đan của bản công tử, đó chính là phúc phận tu hành tám kiếp của đám kiến hôi các ngươi!" """
                )
            ]
        ),
        (
            "HỒI III - CẢNH 6: SỰ HY SINH VÀ THỨC TỈNH",
            "scene-06",
            [
                (
                    "Lối Thoát Bị Phát Hiện",
                    "Lâm Mặc kéo Tiểu Thạch Đầu chạy về Lò Số Chín",
                    "Hai tên chấp sự Trúc Cơ chặn đường tẩu thoát",
                    "action", 100,
                    """Người Kể Chuyện: Giữa lúc đại điện hỗn loạn tiếng gào khóc, Lâm Mặc nắm chặt tay Tiểu Thạch Đầu, kéo cậu bé lùi dần về phía góc khuất của Lò Số Chín. Ở đó có một lối thoát hiểm ngầm dẫn thẳng xuống mạch dung nham sâu dưới lòng đất mà Lâm Mặc đã âm thầm dùng đao cùn đào bới suốt ba năm qua. Thế nhưng, giữa một biển người đang bốc lên huyết vụ đỏ rực, việc hai người Lâm Mặc không hề phát ra sương máu đã lập tức lọt vào mắt của hai tên chấp sự Trúc Cơ Sơ Kỳ đang đứng canh gác trận pháp."""
                ),
                (
                    "Tiểu Thạch Đầu Ngã Xuống",
                    "Tấm lưng nhỏ bé chắn phi kiếm cho huynh trưởng",
                    "Tiểu Thạch Đầu gục ngã trong vòng tay Lâm Mặc",
                    "character", 680,
                    """Người Kể Chuyện: "Hai tên phế vật kia, muốn chạy trốn sao?" Tên chấp sự gầm lên, vung tay phóng xuất thanh phi kiếm sắc bén rít gió xé không khí lao thẳng tới gáy Lâm Mặc. Trong tích tắc ngàn cân treo sợi tóc, để không bại lộ tu vi thật trước mắt Triệu Vô Cực, Lâm Mặc nghiêng người né tránh. Nhưng cậu không ngờ rằng, Tiểu Thạch Đầu đã bất thần lao cả thân hình nhỏ bé ra phía sau lưng cậu. PHẬP! Mũi phi kiếm lạnh buốt đâm xuyên qua lồng ngực gầy guộc của cậu bé. Máu tươi trào ra ướt đẫm vạt áo rách của Lâm Mặc.
Tiểu Thạch Đầu: "Mặc ca... đệ không có linh căn tốt... đệ không thể bước ra ngoài ngắm thế giới được rồi... Huynh... huynh phải sống... phải lên đỉnh Thanh Vân ngắm mặt trời rực rỡ thay phần đệ..."
Người Kể Chuyện: Bàn tay nhỏ bé của cậu bé buông thõng xuống nền đá lạnh. Đôi mắt trong veo từ từ khép lại."""
                ),
                (
                    "Hai Ngón Tay Bẻ Gãy Phi Kiếm",
                    "Cơn thịnh nộ bùng phát sau mười năm ẩn nhẫn",
                    "Lâm Mặc bẻ đôi phi kiếm thượng phẩm như cành củi khô",
                    "action", 1260,
                    """Người Kể Chuyện: Toàn bộ không gian như ngưng đọng lại trong ba giây tĩnh lặng đến rợn người. Lâm Mặc từ từ đặt thi thể Tiểu Thạch Đầu xuống một góc lò sạch sẽ. Cậu đứng dậy, tiếng xương khớp toàn thân kêu răng rắc ròn rã như sấm rền giữa trời quang. Tên chấp sự cười gằn, phóng tiếp một thanh phi kiếm thượng phẩm nhắm thẳng vào mi tâm cậu. Nhưng khi mũi kiếm chỉ còn cách trán Lâm Mặc đúng một tấc, nó đột ngột khựng lại giữa hư không! Lâm Mặc chỉ đưa hai ngón tay đen sạm vì muội than lên, kẹp chặt lấy lưỡi kiếm. RẮC! Thanh phi kiếm thượng phẩm vỡ đôi như một cành củi khô mục nát!
Lâm Mặc: "Chính đạo các ngươi... luyện đan bằng máu thịt của đồng môn. Vậy thì đêm nay, Lâm Mặc ta lấy mạng của toàn bộ lũ súc sinh các ngươi... để tế lò!" """
                )
            ]
        ),

        # =========================================================================
        # HỒI 4: PHẾ ĐAN NGHỊCH THIÊN (Phút 17:30 – 26:00)
        # =========================================================================
        (
            "HỒI IV - CẢNH 7: TRẢM SÁT THIÊN TÀI",
            "scene-07",
            [
                (
                    "Khí Tức Bùng Nổ Vỡ Đê",
                    "Trúc Cơ Đại Viên Mãn và vạn đường vân tử kim",
                    "Lâm Mặc xé toạc áo rách giải phóng toàn bộ khí tức",
                    "character", 100,
                    """Người Kể Chuyện: XOẸT! Lâm Mặc vung tay xé toạc tấm áo tạp dịch rách nát. Trên lồng ngực và cánh tay rắn rỏi của cậu, hàng vạn đường kinh mạch màu đen tím bỗng bừng sáng rực rỡ, chuyển hóa thành màu tử kim chói lòa như thần giáp! Khí tức Luyện Khí tầng ba của kẻ phế vật bỗng chốc bùng nổ như đê vỡ ngàn năm: Luyện Khí tầng chín... Trúc Cơ Sơ Kỳ... Trúc Cơ Trung Kỳ... Trúc Cơ Đại Viên Mãn đỉnh phong! Hai tên chấp sự chưa kịp thốt lên một tiếng kêu cứu thì một luồng hắc hỏa tử độc từ lòng bàn tay Lâm Mặc đã quét qua, thiêu rụi cả xác lẫn hồn phách của chúng thành tro bụi trong chớp mắt!"""
                ),
                (
                    "Phệ Độc Chưởng - Vạn Đan Phần Thiên",
                    "Mười năm độc tố ăn mòn Thanh Vân Kiếm Quyết",
                    "Nắm đấm hắc hỏa đập tan chín đạo kiếm ảnh của Sở Thiên Kiêu",
                    "action", 680,
                    """Người Kể Chuyện: Sở Thiên Kiêu trên đài cao kinh hãi bật dậy, khuôn mặt tuấn tú vặn vẹo vì sững sờ và nhục nhã.
Sở Thiên Kiêu: "Ngươi dám che giấu tu vi trong cấm địa?! Nhưng dù là Trúc Cơ Viên Mãn thì một tên tạp dịch hèn mọn làm sao chống lại được Thanh Vân Kiếm Quyết của bản công tử! Chết đi!"
Người Kể Chuyện: Sở Thiên Kiêu rút bảo kiếm gia truyền, chém ra chín đạo kiếm ảnh xanh biếc như chín con thanh long xé toạc hư không giáng xuống. Đối mặt với kiếm chiêu tuyệt đỉnh, Lâm Mặc không hề lùi bước. Cậu dậm chân nứt toác mặt đất, tung một quyền hủy thiên diệt địa: Phệ Độc Chưởng - Vạn Đan Phần Thiên! Mười năm độc tố của hàng vạn viên phế đan cô đọng lại nổ tung, biến thành biển lửa đen ngòm ăn mòn toàn bộ kiếm khí, khiến thanh bảo kiếm thượng phẩm của Sở Thiên Kiêu mục nát gãy vụn ngay giữa không trung!"""
                ),
                (
                    "Ném Thiên Tài Vào Lò Luyện Đan",
                    "Phúc phận hóa thành Kim Đan trong Cửu Long Lô",
                    "Lâm Mặc bóp nghẹt cổ Sở Thiên Kiêu quẳng vào miệng lò lửa",
                    "action", 1260,
                    """Người Kể Chuyện: "Đây là tà thuật gì?! Phụ thân ta là Đại Trưởng lão nội môn, ngươi dám..." Sở Thiên Kiêu hoảng loạn tháo lui, nhưng Lâm Mặc đã áp sát như một bóng ma tử thần. Bàn tay phủ đầy hắc hỏa của cậu xuyên thẳng qua lớp linh quang hộ thể, bóp nghẹt lấy yết hầu của vị thiên tài, nhấc bổng hắn lên giữa không trung.
Lâm Mặc: "Lúc nãy ngươi vừa dõng dạc nói... được hóa thành một phần của lò đan là phúc phận tu tám kiếp của phế vật chúng ta mà?"
Người Kể Chuyện: Dứt lời, Lâm Mặc vung mạnh cánh tay, ném thẳng Sở Thiên Kiêu vào trong miệng Cửu Long Huyết Lô đang sôi sục lửa đỏ. Tiếng gào thét kinh hoàng thảm thiết của vị thiên tài kiêu ngạo vang lên vài giây rồi hoàn toàn tắt lịm trong ngọn lửa thiêu đốt tinh huyết."""
                )
            ]
        ),
        (
            "HỒI IV - CẢNH 8: TỬ CHIẾN KIM ĐAN",
            "scene-08",
            [
                (
                    "Cơn Điên Cuồng Của Triệu Vô Cực",
                    "Uy áp Kim Đan Sơ Kỳ triệu hồi chín rồng lửa",
                    "Kim Đan hư ảnh lơ lửng sau lưng Triệu Vô Cực ép nứt cột đá",
                    "character", 100,
                    """Người Kể Chuyện: "Tiểu súc sinh to gan! Ngươi dám hủy đan dược của ta, giết hại đệ tử chân truyền của bản tông!" Triệu Vô Cực gầm lên như dã thú phát điên. Cảnh giới Kim Đan Sơ Kỳ của lão bùng phát toàn diện, uy áp kinh hoàng khiến toàn bộ cột đá chống đỡ đại điện nứt toác từng mảng lớn. Một viên Kim Đan màu vàng kim hư ảo lơ lửng sau lưng lão, phóng ra những luồng linh lực cuồng bạo, điều khiển chín con rồng lửa khổng lồ từ miệng lò Cửu Long gầm thét lao bổ về phía Lâm Mặc.
Khoảng cách giữa Trúc Cơ và Kim Đan là một vực thẳm mênh mông không thể vượt qua. Sức nóng và uy áp khủng khiếp ép Lâm Mặc lùi lại ba bước, khóe môi trào ra máu tươi, lớp da trên cánh tay nứt nẻ rỉ máu."""
                ),
                (
                    "Cú Lật Kèo: Nghịch Chuyển Phệ Chủ Trận",
                    "Mười năm cạo xỉ khắc ấn độc huyết vào 99 chân lò",
                    "Chín con rồng lửa đổi màu tím đen quay đầu cắn xé chủ nhân",
                    "concept", 680,
                    """Người Kể Chuyện: Thế nhưng, đối mặt với cái chết cận kề, Lâm Mặc không hề nao núng mà nở một nụ cười ngạo nghễ, lạnh lẽo.
Lâm Mặc: "Triệu Vô Cực! Ngươi làm Chưởng tọa Địa Hỏa Phòng suốt một trăm năm, nhưng đã bao giờ ngươi chịu hạ mình chui vào đáy lò cạo từng mảng xỉ đan bẩn thỉu chưa? Ngươi thực sự tưởng Cửu Long Huyết Lô này là của ngươi sao?!"
Người Kể Chuyện: Lâm Mặc cắn rách đầu lưỡi, phun một ngụm máu độc đen tuyền xuống sàn, hai tay đập mạnh xuống trận pháp dưới chân Lò Số Chín! Suốt mười năm làm nô lệ cạo xỉ ở chín mươi chín lò phụ, Lâm Mặc đã dùng chính máu độc và linh hồn mình âm thầm khắc họa Nghịch Chuyển Phệ Chủ Trận vào từng chân lò! ẦM! Chín con rồng lửa đang lao tới bỗng khựng lại giữa không trung, toàn bộ ngọn lửa đỏ rực chuyển sang màu tím đen ma quái của vạn độc, rồi quay ngoắt đầu lại lao vào cắn xé chính Triệu Vô Cực!
Triệu Vô Cực: "Không thể nào! Mạch Địa Hỏa ngàn năm tại sao lại nghe lệnh của ngươi?! Trong lửa... trong lửa có độc!" """
                ),
                (
                    "Cự Kiếm Trảm Nát Kim Đan",
                    "Thân xác lão trưởng lão tan thành tro bụi",
                    "Lâm Mặc vung thanh cự kiếm mười trượng chém nát Kim Đan",
                    "action", 1260,
                    """Người Kể Chuyện: "Từ mười năm phế đan độc hại mà ngươi bắt ta cạo mỗi ngày đấy! Mọi thứ rác rưởi ngươi chà đạp dưới chân, hôm nay sẽ đích thân tiễn ngươi xuống hoàng tuyền!" Lâm Mặc đạp lên hư không, bước đi giữa biển lửa màu tím đen. Cậu vung hai tay, hợp nhất toàn bộ độc hỏa trong đại điện thành một thanh Cự Kiếm màu đen tím khổng lồ dài mười trượng rực sáng rực rỡ, chém thẳng xuống đỉnh đầu lão trưởng lão gian ác!
OÀNH! Tiếng nổ kinh thiên động địa vang lên xé toạc cả lòng núi. Viên Kim Đan mà Triệu Vô Cực dày công tu luyện hơn hai trăm năm vỡ vụn thành trăm ngàn mảnh sáng. Thân xác của lão trưởng lão bị độc hỏa thiêu rụi thành tro bụi ngay trên đài cao."""
                )
            ]
        ),

        # =========================================================================
        # HỒI 5: BƯỚC RA KHỎI VỰC THẲM (Phút 26:00 – 30:00)
        # =========================================================================
        (
            "HỒI V - CẢNH 9: LUYỆN HÓA KIM ĐAN",
            "scene-09",
            [
                (
                    "Viên Đan Dược Dị Bảo Xuất Thế",
                    "Tinh huyết thiên tài và mảnh vỡ Kim Đan kết tụ",
                    "Viên đan đỏ tím to bằng nắm tay tỏa hào quang ngút trời",
                    "concept", 100,
                    """Người Kể Chuyện: Sau tiếng nổ vang dội trời đất, đại điện Địa Hỏa Phòng sụp đổ một nửa, đất đá rơi rụng ngổn ngang. Bên trong lòng chiếc đỉnh Cửu Long Lô bị xé toạc, một viên đan dược màu đỏ tím to bằng nắm tay từ từ bay lơ lửng lên không trung. Viên đan tỏa ra mùi hương kỳ dị ngạt ngào và nguồn linh lực cuồng bạo chưa từng thấy trong nhân gian. Đó là sự dung hợp hoàn hảo giữa tinh huyết thuần khiết của thiên tài Sở Thiên Kiêu, toàn bộ mảnh vỡ tu vi Kim Đan của Triệu Vô Cực và vạn độc chi hỏa mười năm của Lâm Mặc."""
                ),
                (
                    "Nuốt Đan Đột Phá Cảnh Giới",
                    "Độc Hỏa Kim Đan chính thức ngưng tụ trong đan điền",
                    "Lâm Mặc nuốt chửng viên linh đan nóng bỏng",
                    "character", 680,
                    """Người Kể Chuyện: Không một chút do dự hay sợ hãi, Lâm Mặc vươn bàn tay đầy vết sẹo chụp lấy viên đan nóng rực như than hồng, nuốt thẳng vào bụng. Dược lực cuồng bạo như sông cuộn biển gầm lập tức tràn ngập khắp tứ chi bách mạch. Khí tức của cậu điên cuồng dâng trào, phá vỡ xiềng xích cuối cùng của phàm nhân. Trong đan điền của Lâm Mặc, một viên Độc Hỏa Kim Đan màu tím đen hoàn mỹ lấp lánh chính thức ngưng tụ thành hình!"""
                ),
                (
                    "Cột Sáng Xuyên Thủng Vòm Đá",
                    "Phá tan ngàn trượng đá đen thông lên trời cao",
                    "Cột sáng tử kim bắn thẳng lên trời làm rung chuyển tiên môn",
                    "action", 1260,
                    """Người Kể Chuyện: OÀNH! Một cột sáng màu tử kim rực rỡ từ trên người Lâm Mặc bắn thẳng lên trần hang, phá nát lớp đá đen dày ngàn trượng của Địa Hỏa Phong, tạo thành một lỗ hổng khổng lồ thông thẳng lên trời xanh. Toàn bộ núi non của Thanh Vân Tông rung chuyển dữ dội, báo hiệu sự ra đời của một cỗ sức mạnh nghịch thiên xuất thế từ đống tro tàn."""
                )
            ]
        ),
        (
            "HỒI V - CẢNH 10: ÁNH BÌNH MINH TRÊN ĐỈNH THANH VÂN",
            "scene-10",
            [
                (
                    "Bước Lên Từ Đáy Vực Thẳm",
                    "Cõng thi thể Tiểu Thạch Đầu bước đi trên hư không",
                    "Lâm Mặc bước lên miệng hố giữa sự bao vây của ngàn kiếm tu",
                    "character", 100,
                    """Người Kể Chuyện: Đỉnh Địa Hỏa Phong sụp đổ hoàn toàn giữa thanh thiên bạch nhật, khói bụi bốc lên ngút ngàn tầng mây. Hàng trăm đệ tử nội môn và các vị trưởng lão quyền uy của Thanh Vân Tông ngự kiếm bay tới bao vây kín mít miệng hố sâu thẳm. Từ dưới vực sâu ngập tràn tro tàn và dung nham đỏ lửa, Lâm Mặc bình thản bước từng bước trên hư không đi lên. Trên lưng cậu cõng thi thể của Tiểu Thạch Đầu được bọc cẩn thận trong một tấm áo choàng sạch sẽ. Bàn tay phải của cậu cầm nửa mảnh lệnh bài Chưởng tọa vỡ nát của Triệu Vô Cực.
Chưởng Giáo: "Nghiệt súc to gan! Kẻ nào dám hủy hoại Địa Hỏa Đan Phòng, sát hại trưởng lão và đệ tử chân truyền của bản tông?!" """
                ),
                (
                    "Món Nợ Một Mạng Người",
                    "Ném lệnh bài vỡ và lời thề Nguyên Anh ngày trở lại",
                    "Lâm Mặc đối mặt chưởng giáo dưới ánh bình minh rực rỡ",
                    "action", 680,
                    """Người Kể Chuyện: Lần đầu tiên sau mười năm tăm tối, ánh mặt trời bình minh rực rỡ chiếu rọi lên khuôn mặt góc cạnh, phong trần và ánh mắt kiên định của người thiếu niên. Lâm Mặc lạnh lùng ném nửa mảnh lệnh bài xuống đáy vực sâu.
Lâm Mặc: "Tạp dịch Lò Số Chín - Lâm Mặc! Hôm nay ta trả lại áo tạp dịch, xóa sổ Địa Hỏa Phong nhơ bẩn khỏi thế gian! Từ nay về sau, Thanh Vân Tông các ngươi nợ ta một mạng người! Đợi ngày ta bước lên cảnh giới Nguyên Anh, ta sẽ quay lại ngọn núi này... tính sổ cả gốc lẫn lãi với các ngươi!" """
                ),
                (
                    "Ngọn Lửa Thiêu Rụi Bầu Trời",
                    "Lưu quang tử kim xé toạc hộ sơn đại trận",
                    "Đạo quang tử kim bay vút về phía chân trời xa thẳm",
                    "scene", 1260,
                    """Người Kể Chuyện: Vút! Dứt lời, Lâm Mặc hóa thành một đạo lưu quang màu tử kim xé rách không gian, đâm thủng đại trận hộ sơn của Thanh Vân Tông, bay thẳng về phía chân trời xa xăm trước sự sững sờ kinh hãi của hàng ngàn tu sĩ.
Chân tiên không sinh ra từ lầu son gác tía tráng lệ. Kẻ bước ra từ đống tro tàn dưới đáy lò đan, mới là kẻ hiểu rõ nhất... ngọn lửa nào mới thực sự có thể thiêu rụi cả bầu trời!"""
                )
            ]
        )
    ]

    beats = []
    beat_counter = 1

    for ch_idx, (chapter_badge, scene_id, chapter_beats) in enumerate(chapters, start=1):
        for b_title, b_subhead, b_label, b_type, b_x, raw_text in chapter_beats:
            beat_id = f"beat_{beat_counter:02d}"
            beat_obj = {
                "id": beat_id,
                "role": f"scene_{ch_idx:02d}_beat_{len(beats)%3 + 1}",
                "rawText": raw_text.strip(),
                "visual": {
                    "headline": b_title,
                    "subhead": b_subhead,
                    "badge": chapter_badge,
                    "label": b_label,
                    "sceneId": scene_id,
                    "type": b_type,
                    "region": {
                        "x": b_x,
                        "y": 80,
                        "width": 550,
                        "height": 920
                    }
                }
            }
            beats.append(beat_obj)
            beat_counter += 1

    job_data = {
        "jobId": "job-phe-dan-nghich-thien",
        "title": "Phế Đan Nghịch Thiên (Tro Tàn Địa Hỏa)",
        "workshop": "whiteboard",
        "archetype": "storytelling",
        "targetPlatform": "youtube_long",
        "canvas": {
            "width": 1920,
            "height": 1080,
            "fps": 30
        },
        "voice": {
            "provider": "edge-tts",
            "voiceId": "vi-VN-NamMinhNeural",
            "speed": 0.85,
            "rate": "-15%",
            "pitch": "-2Hz",
            "volume": "+0%"
        },
        "metadata": {
            "genre": "Tu tiên, Huyền huyễn, Phản kích, Hắc ám (Dark Fantasy)",
            "durationExpectedMinutes": 30,
            "author": "Omni-Director",
            "characters": [
                "Lâm Mặc (20 tuổi, Tạp dịch cạo xỉ đan, Trúc Cơ Đỉnh Phong)",
                "Triệu Vô Cực (hơn 200 tuổi, Chưởng tọa Địa Hỏa Đan Phòng, Kim Đan Sơ Kỳ)",
                "Sở Thiên Kiêu (22 tuổi, Đệ tử chân truyền, Trúc Cơ Hậu Kỳ)",
                "Tiểu Thạch Đầu (15 tuổi, Tạp dịch thiếu niên)",
                "Người Kể Chuyện (Dẫn truyện điện ảnh)",
                "Chưởng Giáo (Chưởng giáo Thanh Vân Tông)",
                "Tạp Dịch (Đệ tử tạp dịch Lò Đan)"
            ],
            "characters_voice": {
                "lâm mặc": { "voice": "vi-VN-NamMinhNeural", "rate": "-12%", "pitch": "-3Hz", "volume": "+0%" },
                "mặc ca": { "voice": "vi-VN-NamMinhNeural", "rate": "-12%", "pitch": "-3Hz", "volume": "+0%" },
                "triệu vô cực": { "voice": "vi-VN-NamMinhNeural", "rate": "-16%", "pitch": "-6Hz", "volume": "+0%" },
                "trưởng lão": { "voice": "vi-VN-NamMinhNeural", "rate": "-16%", "pitch": "-6Hz", "volume": "+0%" },
                "sở thiên kiêu": { "voice": "vi-VN-NamMinhNeural", "rate": "-2%", "pitch": "+2Hz", "volume": "+0%" },
                "sở công tử": { "voice": "vi-VN-NamMinhNeural", "rate": "-2%", "pitch": "+2Hz", "volume": "+0%" },
                "tiểu thạch đầu": { "voice": "vi-VN-HoaiMyNeural", "rate": "+0%", "pitch": "+4Hz", "volume": "+0%" },
                "chưởng giáo": { "voice": "vi-VN-NamMinhNeural", "rate": "-18%", "pitch": "-5Hz", "volume": "+0%" },
                "chấp sự": { "voice": "vi-VN-NamMinhNeural", "rate": "-8%", "pitch": "-2Hz", "volume": "+0%" },
                "tạp dịch": { "voice": "vi-VN-NamMinhNeural", "rate": "+0%", "pitch": "+0Hz", "volume": "+0%" },
                "người kể chuyện": { "voice": "vi-VN-NamMinhNeural", "rate": "-15%", "pitch": "-2Hz", "volume": "+0%" },
                "dẫn truyện": { "voice": "vi-VN-NamMinhNeural", "rate": "-15%", "pitch": "-2Hz", "volume": "+0%" }
            },
            "tags": [
                "tutien",
                "huyenhuyen",
                "phedannghichthien",
                "whiteboard",
                "audiodrama",
                "truyenaudio",
                "trotandiahoa",
                "omnivideo"
            ]
        },
        "beats": beats
    }

    with open(job_output, "w", encoding="utf-8") as f:
        json.dump(job_data, f, ensure_ascii=False, indent=2)

    total_words = sum(len(b["rawText"].split()) for b in beats)
    print(f"[OK] Da tao thanh cong file: {job_output}")
    print(f"[*] Tong so beats: {len(beats)}")
    print(f"[*] Tong so tu thoai: {total_words} tu")
    return job_output

if __name__ == "__main__":
    build_job()
