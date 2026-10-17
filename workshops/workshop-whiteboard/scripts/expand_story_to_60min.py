#!/usr/bin/env python3
"""
Tự động mở rộng và hoàn thiện kịch bản Bản Hợp Đồng 100 Tỷ lên đúng chuẩn 60 Phút (~11.500 từ).
Đảm bảo chất lượng văn phong ngôn tình đô thị sâu sắc, cảm động, giàu hình ảnh và kịch tính.
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def build_epic_60min():
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    job_output = root_dir / "output" / "jobs" / "job-hop-dong-100-ty-tong-tai.json"
    doc_output = root_dir / "docs" / "kich-ban-tong-tai-1-tieng.md"

    # Dữ liệu 9 chương với mỗi chương ~1250 - 1300 từ (Tổng 9 chương = ~11.500 từ)
    chapters = [
        # CHƯƠNG 1
        (
            "CHƯƠNG I: ĐÊM MƯA ĐỊNH MỆNH",
            [
                (
                    "Đêm Mưa Định Mệnh",
                    "Thẩm Nhược Hy và bước đường cùng cứu cha",
                    "Nhược Hy chạy dưới mưa trước cổng bệnh viện",
                    "scene", 100,
                    """Người Kể Chuyện: Mười một giờ đêm ở thành phố cảng, cơn mưa rào trái mùa xối xả trút xuống mặt đường nhựa đen nhánh như muốn nuốt chửng mọi ánh đèn le lói của đô thị phồn hoa. Tiếng sấm chớp đùng đoàng xé toạc bầu trời đêm âm u, những hạt mưa quất rát bỏng vào da thịt của người đi đường. Những cơn gió lạnh rít qua từng ngõ ngách, cuốn theo những chiếc lá vàng mục nát. Trước cổng Bệnh viện Đa khoa Trung ương, một bóng dáng thanh mảnh đang chạy loạng choạng dưới màn mưa buốt giá. Đó là Thẩm Nhược Hy. Chiếc áo sơ mi trắng mỏng manh ướt sũng dán chặt vào bờ vai run rẩy, mái tóc dài bết lại bên gò má tái nhợt vì lạnh và kiệt sức. Đôi mắt trong veo như làn nước mùa thu của cô giờ đây đỏ hoe, ngập tràn nước mắt hòa lẫn nước mưa cay xè. Trên tay cô, xấp giấy thông báo viện phí cấp cứu và lệnh cưỡng chế phát mại tài sản của gia tộc họ Thẩm bị nước mưa làm nhòe nhoẹt từng dòng chữ.
Thẩm Nhược Hy: "Ba ơi... xin ba hãy ráng đợi con... Con nhất định sẽ không để người ta rút ống thở của ba... Dù có phải đánh đổi bằng cả sinh mạng này, con cũng phải kiếm đủ năm trăm triệu tiền phẫu thuật đêm nay... Xin ông trời rủ lòng thương, đừng cướp đi người thân duy nhất của con..."
Người Kể Chuyện: Chỉ trong vòng một tuần ngắn ngủi, thế giới tươi đẹp của cô thiên kim tiểu thư ngày nào đã hoàn toàn sụp đổ thành tro bụi. Cha cô, Thẩm lão gia, người cả đời làm việc thiện và gầy dựng nên công ty dược phẩm gia truyền Thẩm Thị, đột ngột bị nhồi máu cơ tim nguy kịch. Nguyên nhân là do chính người em ruột Thẩm Minh Viễn cấu kết với đối thủ bên ngoài rút ruột toàn bộ cổ phần, làm giả chữ ký bảo lãnh khiến Thẩm gia gánh món nợ hai mươi tỷ đồng. Đêm nay, nếu không nộp đủ năm trăm triệu tiền phẫu thuật đặt stent tim khẩn cấp, bệnh viện sẽ buộc phải ngừng máy trợ tim. Cô đã gõ cửa từng người quen, từng đối tác từng cúi đầu cung kính trước cha cô, nhưng đáp lại chỉ là những cái nhìn khinh miệt, những cánh cửa đóng sầm lạnh lùng và những lời xua đuổi cay nghiệt như xát muối vào tim."""
                ),
                (
                    "Tổng Tài Lục Cảnh Thâm",
                    "Cơn mất ngủ và đau đầu kinh niên hành hạ",
                    "Lục Cảnh Thâm ôm đầu trong khoang xe sang trọng",
                    "character", 680,
                    """Người Kể Chuyện: Cùng lúc đó, tại ngã tư đại lộ ven sông, một đoàn xe đen sang trọng đang lao vút đi trong đêm giông bão. Dẫn đầu là chiếc Maybach màu đen tuyền mang biển số tứ quý độc nhất vô nhị. Bên trong khoang xe bọc da thượng hạng êm ái, không khí đặc quánh sự ngột ngạt và áp lực đến nghẹt thở. Ngồi ở hàng ghế sau là Lục Cảnh Thâm, người đàn ông quyền lực nhất thương trường Phương Nam, Chủ tịch đương nhiệm của Tập đoàn tài phiệt Lục Thị. Anh khoác trên mình bộ âu phục đen đặt may thủ công từ Savile Row, từng đường nét trên khuôn mặt tựa như tạc bằng đá hoa cương, sắc bén, kiêu dũng và không hề có một chút biểu cảm ấm áp nào. Thế nhưng lúc này, đôi mày kiếm của anh nhíu chặt lại, các khớp ngón tay nắm chặt lấy tay vịn đến mức trắng bệch. Một cơn đau nửa đầu dữ dội như ngàn mũi kim châm đang cắn xé từng tế bào thần kinh của anh, biến bóng đêm thành một địa ngục trần gian.
Lục Cảnh Thâm: "Giang Thừa... thuốc... thuốc an thần của tôi đâu?"
Trợ Lý Giang: "Lục tổng! Bác sĩ trưởng đã cảnh báo liều lượng tháng này của ngài đã vượt ngưỡng an toàn gấp ba lần rồi! Nếu ngài uống thêm một viên nào nữa sẽ trụy tim, nguy hiểm trực tiếp đến tính mạng! Đã bốn ngày bốn đêm ngài không hề chợp mắt được một phút nào rồi, xin ngài hãy cố chịu đựng một chút, chúng ta sắp về tới Ngự Cảnh Uyển rồi!"
Lục Cảnh Thâm: "Câm miệng! Cậu có biết cảm giác như có chiếc búa tạ nện liên tục vào hộp sọ là thế nào không? Tôi bảo cậu... lấy thuốc ra đây ngay lập tức!"
Người Kể Chuyện: Lục Cảnh Thâm mắc chứng mất ngủ và rối loạn cảm giác đau đớn kinh niên suốt mười năm qua, kể từ sau vụ tai nạn thảm khốc cướp đi sinh mạng của cha mẹ anh trong một đêm đông bão tuyết. Với anh, bóng đêm là một nhà tù không lối thoát, nơi ký ức rỉ máu luôn chực chờ nuốt chửng linh hồn anh. Không một loại thuốc an thần nào trên thế giới còn đủ sức xoa dịu những cơn co giật thần kinh của người đàn ông quyền lực bậc nhất này."""
                ),
                (
                    "Chạm Tay Định Mệnh",
                    "Cơn đau dịu đi và sự tiếp xúc kỳ diệu dưới mưa",
                    "Khoảnh khắc hai bàn tay chạm nhau dưới làn mưa",
                    "concept", 1260,
                    """Người Kể Chuyện: Bất ngờ, từ con hẻm bên đường, một bóng người gầy guộc ôm xấp giấy tờ lao vọt ra giữa làn xe. Tài xế chiếc Maybach hoảng hốt đạp lút phanh và bẻ ngoặt tay lái. Tiếng lốp xe nghiến rít chói tai trên mặt đường trơn trượt. Chiếc xe trượt dài một đoạn rồi dừng khựng lại, mũi xe chỉ cách người Nhược Hy vài centimet. Cú phanh gấp khiến xấp hồ sơ viện phí trên tay cô bay tung tóe giữa màn mưa đêm. Nhược Hy ngã ngồi xuống vũng nước lạnh, toàn thân run rẩy nhưng hai tay vẫn cố ôm chặt lấy tập bệnh án của cha.
Trợ Lý Giang: "Cô gái! Cô có làm sao không? Sao lại lao ra đường lúc mưa gió nguy hiểm thế này!"
Thẩm Nhược Hy: "Tôi... tôi xin lỗi... Tôi vội đến bệnh viện quá... Xin thứ lỗi vì làm phiền các anh..."
Người Kể Chuyện: Cánh cửa sau xe bật mở. Chiếc ô đen lớn che khuất tầm nhìn, đôi giày da đắt tiền dẫm lên mặt nước đọng. Lục Cảnh Thâm bước xuống. Ánh mắt anh nhìn cô gái ướt sũng dưới chân mình đầy vẻ chán ghét quen thuộc của một tổng tài thường xuyên bị các tiểu thư giả vờ va chạm để tiếp cận.
Lục Cảnh Thâm: "Lại là trò diễn kịch vụng về. Giang Thừa, vứt cho cô ta năm mươi triệu rồi đi, tôi không rảnh dây dưa với những kẻ dùng thủ đoạn rẻ tiền này."
Thẩm Nhược Hy: "Anh nói ai dùng thủ đoạn rẻ tiền? Tôi bị trượt chân ngã! Tôi không cần thứ tiền bố thí xấc xược của anh! Tránh ra cho tôi đi cứu cha tôi!"
Người Kể Chuyện: Trong cơn tức giận uất nghẹn, Nhược Hy vung tay gạt mạnh chiếc ô. Đầu ngón tay mềm mại và ấm áp kỳ lạ của cô vô tình chạm lướt qua mu bàn tay lạnh ngắt như băng của Lục Cảnh Thâm. Một khoảnh khắc tĩnh lặng kỳ diệu bỗng ập đến. Ngay giây phút da thịt chạm nhau, cơn đau đầu búa bổ như sóng cuộn trong tâm trí Lục Cảnh Thâm đột ngột dịu xuống một nhịp. Mùi hương hoa nhài thanh khiết quyện cùng hơi nước mưa từ người cô gái làm dịu đi cảm giác bức bối nghẹt thở đã hành hạ anh suốt bốn ngày qua. Cảnh Thâm sững sờ, đồng tử co rút nhìn chằm chằm vào cô gái bé nhỏ đang ôm ngực thở dốc trước mặt mình. Lần đầu tiên trong mười năm, anh cảm nhận được một luồng hơi ấm bình yên đến run rẩy."""
                )
            ]
        ),

        # CHƯƠNG 2
        (
            "CHƯƠNG II: BẢN HỢP ĐỒNG 100 TỶ",
            [
                (
                    "Cuộc Đàm Phán Tầng 68",
                    "Giao kèo hôn nhân một năm tại Lục Thị Tower",
                    "Tập hợp đồng hôn nhân mạ vàng trên bàn làm việc",
                    "concept", 100,
                    """Người Kể Chuyện: Chín giờ sáng ngày hôm sau, tại phòng bệnh hồi sức tích cực Bệnh viện Trung ương, Nhược Hy nhận được tin sét đánh: toàn bộ chi phí cấp cứu đêm qua của cha cô đã được một nhân vật bí ẩn thanh toán. Người đó không ai khác chính là Lục Cảnh Thâm. Trợ lý Giang Thừa xuất hiện với một lá thư mời mạ vàng, yêu cầu cô có mặt tại trụ sở Tập đoàn Lục Thị đúng mười giờ sáng. Hai tiếng sau, Nhược Hy đứng trước văn phòng Chủ tịch tầng sáu mươi tám của tòa tháp cao nhất thành phố. Toàn bộ vách tường là kính cường lực bao quát toàn cảnh thương thành tráng lệ phía dưới. Lục Cảnh Thâm ngồi sau chiếc bàn làm việc bằng gỗ mun nguyên khối, trên người là chiếc áo sơ mi đen phẳng phiu không một nếp nhăn. Ánh mắt thâm sâu như giếng cổ nhìn chằm chằm vào cô gái nhỏ bé nhưng tràn đầy vẻ kiên cường.
Lục Cảnh Thâm: "Ngồi đi. Tôi không thích nói chuyện với người đứng."
Thẩm Nhược Hy: "Cảm ơn Lục tổng đã chi tiền cứu cha tôi đêm qua. Năm trăm triệu đó tôi nhất định sẽ đi làm kiếm tiền trả lại cả gốc lẫn lãi cho anh. Nhưng nếu anh gọi tôi đến đây để ra điều kiện mua vui hay sỉ nhục nhân phẩm của tôi, thì anh đã lầm người rồi."
Lục Cảnh Thâm: "Cô đánh giá bản thân mình quá cao rồi đấy. Đọc tập tài liệu trên bàn đi rồi hãy mở miệng."
Người Kể Chuyện: Nhược Hy nghi hoặc cầm tập tài liệu bìa da viền vàng lên. Ngay trang đầu tiên, dòng chữ in hoa đập vào mắt cô: HỢP ĐỒNG HÔN NHÂN CHIẾN LƯỢC – THỜI HẠN BA TRĂM SÁU MƯƠI LĂM NGÀY. Toàn bộ nội dung giao kèo được trình bày rõ ràng với những điều khoản kinh tế chấn động."""
                ),
                (
                    "Điều Khoản Một Trăm Tỷ",
                    "Cái giá của sự tự do và sức khỏe của người cha",
                    "Nhược Hy xem xét từng điều khoản hợp đồng",
                    "character", 680,
                    """Người Kể Chuyện: Bản hợp đồng quy định: Thứ nhất, Thẩm Nhược Hy đồng ý kết hôn hợp pháp trên danh nghĩa với Lục Cảnh Thâm trong vòng một năm, đóng vai một người vợ mẫu mực, yêu thương chồng trước mặt truyền thông và gia tộc họ Lục. Thứ hai, cô phải chuyển đến sinh sống tại biệt phủ Ngự Cảnh Uyển, có mặt bên cạnh mỗi khi Lục Cảnh Thâm lên cơn mất ngủ và đau nửa đầu. Đổi lại, Lục Cảnh Thâm sẽ thanh toán toàn bộ món nợ hai mươi tỷ của Thẩm gia, chi trả toàn bộ chi phí điều trị phục hồi y tế tốt nhất thế giới cho cha cô, và chuyển vào tài khoản cá nhân của cô đúng một trăm tỷ đồng khi hợp đồng kết thúc.
Thẩm Nhược Hy: "Kết hôn giả một năm? Trị giá một trăm tỷ đồng? Lục tổng, người muốn gả cho anh xếp hàng dài từ Nam chí Bắc, tại sao anh lại chọn một cô gái sa cơ lụi bại, gia đình mang nợ như tôi?"
Lục Cảnh Thâm: "Thứ nhất, bà nội tôi tuổi cao sức yếu, tâm nguyện duy nhất lúc này là muốn nhìn thấy tôi yên bề gia thất với một cô gái gia thế trong sạch, có học thức. Thứ hai, những tiểu thư quyền quý ngoài kia tiếp cận tôi chỉ vì chiếc ghế Thiếu phu nhân Lục Thị, họ sẽ tìm mọi cách trói buộc tôi. Còn cô, cô chỉ cần tiền để cứu mạng cha mình. Kẻ có mục đích rõ ràng và lòng tham có giới hạn sẽ dễ kiểm soát hơn rất nhiều."
Người Kể Chuyện: Cảnh Thâm đứng dậy, từng bước tiến sát lại gần cô. Bóng dáng cao lớn của anh phủ bóng xuống người Nhược Hy, mang theo mùi hương gỗ tuyết tùng trầm ấm đầy áp lực."""
                ),
                (
                    "Cam Kết Son Sắt",
                    "Hai chữ ký mở ra một định mệnh không thể quay đầu",
                    "Nhược Hy và Cảnh Thâm đặt bút ký tên",
                    "concept", 1260,
                    """Lục Cảnh Thâm: "Và điều quan trọng nhất... tối qua khi tay cô chạm vào tôi, tôi đã ngủ được trọn vẹn hai tiếng đồng hồ mà không cần đến thuốc an thần. Bác sĩ riêng nói trường sinh học và mùi hương của cô có khả năng an thần đặc biệt với hệ thần kinh của tôi. Nói cách khác, cô chính là liều thuốc duy nhất cứu sống giấc ngủ của tôi. Thế nào? Ký vào đây, hoặc bước ra ngoài nhìn cha cô bị rút ống thở ngay chiều nay?"
Thẩm Nhược Hy: "Được... Tôi ký! Nhưng tôi yêu cầu thêm một điều khoản bổ sung: Anh tuyệt đối không được xâm phạm thân thể tôi ngoài việc hỗ trợ giấc ngủ. Và điều quan trọng nhất: Cả hai chúng ta tuyệt đối không được nảy sinh tình cảm thật với nhau!"
Lục Cảnh Thâm: "Yên tâm. Với tôi, phụ nữ chỉ mang lại rắc rối và phiền toái. Tôi không bao giờ có hứng thú yêu đương với một cô gái yếu đuối như cô."
Người Kể Chuyện: Bút ký chạm giấy. Nét mực đen của hai cái tên Lục Cảnh Thâm và Thẩm Nhược Hy đan xen vào nhau trên trang giấy trắng. Một trăm tỷ sính lễ được kích hoạt, hai mươi tỷ nợ nần được xóa sạch trong tích tắc. Một bản giao kèo số phận chính thức bắt đầu, cuốn hai con người xa lạ vào vòng xoáy của danh vọng, bí mật và những rung động ngọt ngào không thể ngờ tới."""
                )
            ]
        ),

        # CHƯƠNG 3
        (
            "CHƯƠNG III: BƯỚC VÀO CỬA HÀO MÔN",
            [
                (
                    "Biệt Phủ Ngự Cảnh Uyển",
                    "Sự xa hoa choáng ngợp và bước chân đầu tiên vào Lục gia",
                    "Toàn cảnh biệt phủ Ngự Cảnh Uyển lộng lẫy trong đêm tiệc",
                    "scene", 100,
                    """Người Kể Chuyện: Hai ngày sau khi đăng ký kết hôn chớp nhoáng, chiếc Rolls-Royce Phantom đưa Thẩm Nhược Hy đến Ngự Cảnh Uyển – khu biệt phủ rộng lớn nằm tách biệt trên sườn đồi nhìn thẳng ra vịnh biển. Lối đi lát đá hoa cương trắng muốt rợp bóng những hàng phong lá đỏ. Hơn năm mươi người hầu và quản gia xếp hàng ngay ngắn hai bên bậc thềm cúi đầu đồng thanh chào đón: Kính chào Thiếu phu nhân! Nhược Hy hít sâu một hơi để trấn tĩnh lồng ngực đang đập liên hồi. Hôm nay cô khoác trên mình chiếc váy dạ hội lụa tơ tằm màu trắng thanh nhã, mái tóc đen nhánh búi lơi cài chiếc trâm ngọc bích – kỷ vật duy nhất mà người mẹ quá cố để lại. Dù không đeo chuỗi kim cương bạc tỷ nào, nhưng cốt cách thanh tao, đoan trang toát ra từ dòng dõi thư hương thế gia nhiều đời khiến bất cứ ai nhìn vào cũng phải thầm thán phục. Đêm nay là đại tiệc mừng thọ lần thứ bảy mươi lăm của Lục Lão phu nhân, quy tụ toàn bộ giới tài phiệt và chính khách máu mặt nhất thương thành."""
                ),
                (
                    "Sự Mỉa Mai Của Kẻ Ghen Ghét",
                    "Triệu Bích Nguyệt và màn khiêu khích chốn đông người",
                    "Nhược Hy đối chất điềm tĩnh trước Triệu Bích Nguyệt",
                    "character", 680,
                    """Người Kể Chuyện: Vừa bước chân vào đại sảnh dát vàng rực rỡ, hàng trăm ánh mắt tò mò, ghen tị và soi mói lập tức đổ dồn về phía Nhược Hy. Những tiếng xì xào to nhỏ vang lên khắp nơi về cô dâu nghèo sa cơ vừa đổi đời chỉ sau một đêm. Từ giữa đám đông, một cô gái trong bộ đầm dạ hội đỏ rực, cổ đeo chuỗi hồng ngọc lộng lẫy bước tới chặn đường cô. Đó là Triệu Bích Nguyệt, ái nữ của Tập đoàn tài chính Triệu Thị, người vốn luôn tự xem mình là vị hôn thê tương lai môn đăng hộ đối nhất của Lục Cảnh Thâm.
Triệu Bích Nguyệt: "Ôi chao, đây chẳng phải là Thẩm tiểu thư nức tiếng của Thẩm thị vừa phá sản sao? À không, bây giờ phải gọi là Lục phu nhân nhỉ? Nghe nói chú ruột cô vừa ôm tiền bỏ trốn, cha cô thì nằm thở oxy sắp chết. Không ngờ cô Thẩm đây lại giỏi leo trèo đến thế, nhanh chân trèo lên được giường của anh Cảnh Thâm để đổi lấy mạng sống cho cả nhà. Thật là một màn hy sinh thân mình rẻ rúng làm sao!"
Thẩm Nhược Hy: "Triệu tiểu thư, Thẩm gia tôi gặp hoạn nạn, tôi làm con dốc lòng cứu cha là trọn đạo hiếu. Còn việc tôi và anh Cảnh Thâm kết hôn là chuyện đại sự của hai bên gia đình, được pháp luật công nhận đàng hoàng. Tôi đường hoàng bước vào đây bằng cửa chính, chẳng hay có điều gì khiến Triệu tiểu thư phải ghen ăn tức ở đến mức đánh mất cả phong thái của một thiên kim khuê các trước mặt bao nhiêu quan khách như vậy?" """
                ),
                (
                    "Vị Thế Của Người Vợ Hợp Pháp",
                    "Lục Cảnh Thâm ra mặt dằn mặt toàn bộ giới tài phiệt",
                    "Lục Cảnh Thâm đứng chắn trước Nhược Hy đầy uy lực",
                    "character", 1260,
                    """Người Kể Chuyện: Bị nói trúng tim đen trước mặt bao nhiêu người, Triệu Bích Nguyệt tức tím mặt, giơ cao ly rượu vang đỏ toan hắt thẳng vào mặt Nhược Hy để làm nhục cô.
Triệu Bích Nguyệt: "Con tiện nhân sa cơ này, mày dám hỗn xược với tao..."
Người Kể Chuyện: Nhưng bàn tay của Triệu Bích Nguyệt chưa kịp hạ xuống thì đã bị một bàn tay cứng như thép nguội chộp chặt giữa không trung. Lực bóp mạnh đến mức khiến cô ta thét lên đau đớn, ly rượu vang rơi choảng xuống sàn gạch vỡ tan tành. Lục Cảnh Thâm xuất hiện. Anh đứng sừng sững chắn ngay trước người Thẩm Nhược Hy, ánh mắt sắc lạnh như dao lam ghim thẳng vào Triệu Bích Nguyệt khiến cả sảnh tiệc bỗng chốc im phăng phắc như tờ.
Lục Cảnh Thâm: "Triệu Bích Nguyệt, ai cho cô cái gan làm loạn trong tiệc mừng thọ của bà nội tôi? Ai cho cô quyền xúc phạm người phụ nữ có tên trên sổ hộ khẩu của Lục Cảnh Thâm này? Cút ra ngoài ngay lập tức! Giang Thừa, thông báo cho toàn bộ các phòng ban: Kể từ hôm nay, nếu gia tộc nào dám có nửa lời bất kính với vợ tôi, Tập đoàn Lục Thị sẽ chấm dứt mọi hợp đồng làm ăn vĩnh viễn!"
Người Kể Chuyện: Cả khán phòng nín thở sợ hãi. Không ai ngờ người đàn ông nổi tiếng tàn nhẫn và vô cảm như Lục Cảnh Thâm lại công khai bảo vệ cô vợ mới cưới dứt khoát đến thế. Phía sau, Lục Lão phu nhân ngồi trên xe lăn mỉm cười đôn hậu, ánh mắt bà nhìn Nhược Hy tràn ngập sự yêu thương và tin tưởng tuyệt đối."""
                )
            ]
        ),

        # CHƯƠNG 4
        (
            "CHƯƠNG IV: ĐÊM MẤT NGỦ & LIỀU THUỐC XOA DỊU",
            [
                (
                    "Căn Phòng Xám Tro",
                    "Đêm đầu tiên tại phòng ngủ chính của tổng tài",
                    "Cảnh Thâm co ro trong cơn ác mộng",
                    "scene", 100,
                    """Người Kể Chuyện: Mười hai giờ đêm tại phòng ngủ chính của biệt thự Ngự Cảnh Uyển. Căn phòng rộng thênh thang hơn một trăm mét vuông được bài trí theo tông màu xám tro tối giản, cách âm tuyệt đối và buốt lạnh đến mức không có lấy một hơi ấm của sự sống. Đúng như bản hợp đồng đã cam kết, Nhược Hy mang chiếc nệm mỏng trải xuống tấm thảm lông cừu dưới sàn nhà bên cạnh giường lớn. Cô ngồi yên lặng nhìn Cảnh Thâm đang ngồi tựa lưng trên ghế bành, chiếc áo sơ mi mở bung hai cúc cổ để lộ lồng ngực vạm vỡ nhưng đôi mắt mỏi mệt vì thiếu ngủ trầm trọng.
Thẩm Nhược Hy: "Tối nay ở bữa tiệc mừng thọ... cảm ơn anh đã ra mặt giúp tôi giải vây."
Lục Cảnh Thâm: "Đừng tự mình đa tình. Tôi bảo vệ cô là để giữ gìn thể diện của Lục gia trước mặt truyền thông, hoàn toàn không liên quan đến cá nhân cô. Hãy nhớ kỹ thân phận của mình, đừng bao giờ ảo tưởng những thứ không thuộc về mình."
Thẩm Nhược Hy: "Tôi biết rõ. Tôi luôn ghi nhớ giá trị của một trăm tỷ đồng mà anh đã chi trả."
Người Kể Chuyện: Căn phòng chìm vào sự tĩnh lặng tịch mịch. Đêm càng về khuya, không khí càng lạnh buốt. Đồng hồ điểm một giờ sáng, khi Nhược Hy đang chập chờn thiếp đi thì từ phía giường ngủ bỗng phát ra những tiếng thở dốc nghẹn ngào cùng sự run rẩy dữ dội."""
                ),
                (
                    "Khúc Hát Ru Trong Đêm Tối",
                    "Sự dịu dàng xoa dịu vết thương tâm lý rỉ máu mười năm",
                    "Nhược Hy vuốt tóc và hát ru cho Cảnh Thâm ngủ",
                    "character", 680,
                    """Người Kể Chuyện: Nhược Hy bật dậy nhìn lên. Dưới ánh đèn ngủ lờ mờ, Lục Cảnh Thâm đang co quắp người lại như một đứa trẻ bị bỏ rơi giữa trời đông giá rét. Hai tay anh ôm chặt lấy đầu, trán đầm đìa mồ hôi lạnh, từng đường gân xanh nổi cộm trên thái dương. Những tiếng rên rỉ nghẹn ngào trong cơn ác mộng thoát ra từ lồng ngực anh:
Lục Cảnh Thâm: "Mẹ ơi... Máu nhiều quá... Đừng bỏ con lại một mình trong hốc tuyết... Lạnh quá... Cứu con với..."
Thẩm Nhược Hy: "Lục Cảnh Thâm! Anh tỉnh lại đi! Lục Cảnh Thâm! Có tôi ở đây rồi, đừng sợ nữa!"
Người Kể Chuyện: Trong cơn hoảng loạn vô thức, Cảnh Thâm bất ngờ vung tay túm chặt lấy cổ tay Nhược Hy, kéo mạnh cô ngã nhào lên ngực anh. Hai cánh tay rắn chắc của anh siết chặt lấy bờ vai cô như một người sắp chết đuối bám chặt lấy khúc gỗ cứu sinh duy nhất giữa biển khơi giông bão. Toàn thân anh run rẩy không ngừng. Nhược Hy toan giãy giụa thoát ra, nhưng khi nhìn thấy giọt nước mắt nóng hổi lăn dài từ khóe mi của người đàn ông kiêu ngạo ấy, trái tim cô bỗng thắt lại một cảm giác xót xa vô bờ bến. Cô nhận ra đằng sau lớp vỏ bọc quyền lực và lạnh lùng kia là một tâm hồn vụn vỡ đang chịu đựng sự đày đọa suốt mười năm dài. Nhược Hy khẽ thở dài, buông lỏng người. Bàn tay nhỏ bé của cô nhẹ nhàng đặt lên thái dương anh, ngón tay luồn qua mái tóc đen dày, khẽ xoa bóp từng huyệt đạo. Rồi cô cất giọng hát khe khẽ, một khúc hát ru êm đềm thời thơ ấu:
Thẩm Nhược Hy: "Gió mùa đông đã qua rồi... Ánh trăng sáng đầu non... Ngủ đi nhé, bình yên đã về bên hiên nhà..." """
                ),
                (
                    "Bình Minh Sau Mười Năm Tăm Tối",
                    "Giấc ngủ sâu đầu tiên trọn vẹn không cần thuốc an thần",
                    "Cảnh Thâm ngủ say bên cạnh Nhược Hy dưới nắng sớm",
                    "scene", 1260,
                    """Người Kể Chuyện: Giọng hát trong trẻo của cô như một dòng suối nước mát tưới lên mảnh đất tâm can đang bốc cháy của Lục Cảnh Thâm. Hương hoa nhài thanh khiết từ cơ thể cô vương vấn quanh đầu mũi anh, làm dịu đi từng dây thần kinh đang căng thẳng tột độ. Kỳ diệu thay, hơi thở hỗn loạn của người đàn ông dần dần chậm rãi và đều đặn trở lại. Những cơn co giật dừng hẳn. Cảnh Thâm buông lỏng các ngón tay, nhưng khuôn mặt vẫn vùi sâu vào hõm cổ ấm áp của Nhược Hy, say sưa chìm vào một giấc ngủ sâu không mộng mị. Nhược Hy ngồi tựa vào thành giường, để mặc cho anh tựa vào mình suốt đêm dài. Sáng hôm sau, những tia nắng mai vàng rực rọi qua khung cửa sổ, chiếu sáng căn phòng ngủ ấm áp. Khi Cảnh Thâm mở mắt ra, đồng hồ đã điểm đúng tám giờ sáng. Mười năm qua, chưa bao giờ anh ngủ một giấc dài tám tiếng liên tục mà không cần đến một viên thuốc ngủ nào. Nhìn cô gái nhỏ bé đang thiếp đi bên cạnh với đôi mắt mệt mỏi nhưng thanh thản, khóe môi của người đàn ông băng giá lần đầu tiên khẽ cong lên một nụ cười ấm áp."""
                )
            ]
        ),

        # CHƯƠNG 5
        (
            "CHƯƠNG V: CẠM BẪY NƠI THƯƠNG TRƯỜNG",
            [
                (
                    "Cơn Bão Rò Rỉ Tài Liệu",
                    "Dự án năm mươi nghìn tỷ bị đánh cắp thông tin cốt lõi",
                    "Phòng họp hội đồng quản trị Lục Thị căng thẳng tột độ",
                    "scene", 100,
                    """Người Kể Chuyện: Ba tháng sau ngày cưới, cuộc sống tại Ngự Cảnh Uyển dần có những chuyển biến ngọt ngào thầm lặng. Mỗi chiều về nhà, Cảnh Thâm đều được thưởng thức những món canh bổ dưỡng do chính tay Nhược Hy nấu theo bài thuốc gia truyền của Thẩm gia. Căn bệnh mất ngủ của anh thuyên giảm rõ rệt, những nụ cười xuất hiện nhiều hơn trên gương mặt lạnh lùng. Thế nhưng, giông bão thương trường bất ngờ ập đến vào một buổi chiều định mệnh. Dự án Cảng Năng lượng Xanh trị giá năm mươi nghìn tỷ đồng – dự án sống còn mang tính chiến lược quốc tế của Tập đoàn Lục Thị bước vào giai đoạn nộp hồ sơ đấu thầu quyết định. Đúng lúc này, bản kế hoạch đấu thầu tuyệt mật và sơ đồ công nghệ lõi bị rò rỉ hoàn toàn ra bên ngoài. Đối thủ cạnh tranh trực tiếp – liên minh của Triệu Thị và Thẩm Minh Viễn đã đưa ra mức giá bỏ thầu thấp hơn Lục Thị đúng 0,1% và nắm trọn toàn bộ công nghệ then chốt. Cả hội đồng quản trị Lục Thị chấn động dữ dội."""
                ),
                (
                    "Cạm Bẫy Vu Oan Giá Họa",
                    "Hình ảnh camera thư phòng và khoản tiền mười tỷ ẩn danh",
                    "Cảnh Thâm đối chất bên xấp tài liệu, Nhược Hy rơi nước mắt",
                    "character", 680,
                    """Người Kể Chuyện: Tại phòng họp khẩn cấp, các cổ đông lớn giận dữ đập bàn chất vấn. Camera an ninh của Ngự Cảnh Uyển được trích xuất trên màn hình lớn: Mười giờ đêm hôm trước, Thẩm Nhược Hy đã bưng khay trà bước vào thư phòng riêng của Cảnh Thâm khi anh đang tắm, nán lại bên bàn làm việc suốt năm phút và mở chiếc ngăn kéo bảo mật chứa con dấu và ổ cứng dự án. Ngay sáng nay, tài khoản thanh toán viện phí của cha cô tại bệnh viện bất ngờ nhận được khoản tiền ẩn danh mười tỷ đồng. Mọi chứng cứ dường như đều chỉ thẳng vào Nhược Hy là gián điệp nội gián do Thẩm gia cài cắm. Cảnh Thâm lái xe lao thẳng về Ngự Cảnh Uyển trong cơn bão lòng dữ dội. Anh ném xấp hồ sơ rò rỉ xuống trước mặt cô.
Lục Cảnh Thâm: "Tối qua cô vào thư phòng của tôi làm gì? Ai đã chuyển mười tỷ vào viện phí của cha cô sáng nay? Giải thích cho tôi!"
Thẩm Nhược Hy: "Tôi chỉ mang trà hoa cúc mật ong vào cho anh! Tôi thấy ngăn kéo bị kẹt hở ra nên mới đẩy lại giúp anh! Cảnh Thâm... ba tháng qua sớm tối bên nhau... trong mắt anh, tôi vẫn chỉ là một kẻ hám tiền, sẵn sàng bán rẻ lương tâm để đâm sau lưng anh sao?"
Lục Cảnh Thâm: "Tôi chỉ tin vào chứng cứ xác thực! Tại sao lại trùng hợp đúng vào đêm hôm qua?" """
                ),
                (
                    "Nước Mắt Của Lòng Tự Trọng",
                    "Sự nghi kỵ và mệnh lệnh điều tra ngầm trong bóng tối",
                    "Cảnh Thâm đứng bên cửa sổ trầm tư nhìn vào màn đêm",
                    "scene", 1260,
                    """Thẩm Nhược Hy: "Nếu anh không tin tôi, cứ việc gọi cảnh sát đến bắt tôi đi! Hoặc là xé bỏ bản hợp đồng này, tôi sẽ trả lại toàn bộ tiền và cút khỏi cuộc đời anh ngay lập tức!"
Người Kể Chuyện: Nhìn những giọt nước mắt uất ức tuôn rơi lã chã trên gương mặt tái nhợt của Nhược Hy, lồng ngực Cảnh Thâm nhói đau như bị bóp nghẹt. Bàn tay anh toan đưa lên lau nước mắt cho cô nhưng lại khựng lại giữa không trung vì sự kiêu hãnh của một người đàn ông đứng đầu đế chế tài phiệt. Anh không báo cảnh sát, cũng không đuổi cô đi, chỉ ra lệnh cho vệ sĩ phong tỏa Ngự Cảnh Uyển để bảo vệ an toàn cho cô. Đêm hôm đó, Cảnh Thâm đứng một mình bên khung cửa sổ thư phòng nhìn vào màn đêm tĩnh mịch, tay cầm chiếc điện thoại ra lệnh đanh thép cho Giang Thừa:
Lục Cảnh Thâm: "Giang Thừa! Huy động toàn bộ lực lượng an ninh mạng và thám tử giỏi nhất cho tôi! Kiểm tra toàn bộ tài khoản ngân hàng của người làm trong biệt thự và các mối quan hệ của Triệu Bích Nguyệt! Tôi không tin người phụ nữ của tôi lại là kẻ phản bội!" """
                )
            ]
        ),

        # CHƯƠNG 6
        (
            "CHƯƠNG VI: LẬT MẶT KẺ PHẢN BỘI",
            [
                (
                    "Đại Tiệc Đắc Thắng Sớm",
                    "Hội trường mở thầu và nụ cười ngạo mạn của kẻ thủ ác",
                    "Triệu Bích Nguyệt tự tin trả lời phỏng vấn truyền thông",
                    "character", 100,
                    """Người Kể Chuyện: Ba ngày tiếp theo là chuỗi ngày đen tối nhất của thị trường tài chính: Cổ phiếu Lục Thị sụt giảm liên tục, phe phái đối lập ép Cảnh Thâm phải từ chức Chủ tịch và tống giam Thẩm Nhược Hy. Sáng ngày mở thầu chính thức tại Trung tâm Hội nghị Quốc gia, hàng trăm phóng viên báo đài trong nước và quốc tế vây kín đại sảnh. Triệu Bích Nguyệt cùng Thẩm Minh Viễn xuất hiện với tư cách người đại diện liên minh trúng thầu, tự tin mở tiệc sâm panh ăn mừng sớm trước ống kính máy quay.
Triệu Bích Nguyệt: "Hôm nay là ngày đánh dấu sự chấm dứt của kỷ nguyên độc quyền họ Lục! Lục Cảnh Thâm vì mê muội một đứa con gái bần hàn mang danh vợ hợp đồng mà làm sụp đổ cả cơ nghiệp trăm năm của tổ tiên để lại! Thật đáng đời!"
Thẩm Minh Viễn: "Đúng vậy! Đứa cháu gái bất hiếu của tôi tưởng trèo cao mà được yên thân sao? Hôm nay công lý sẽ được thực thi!"
Người Kể Chuyện: Đúng lúc hai kẻ thủ ác đang say sưa trong men say chiến thắng, cánh cửa lớn của hội trường bất ngờ bật mở toang."""
                ),
                (
                    "Màn Lật Ngược Thế Cờ Ngoạn Mục",
                    "Sự thật phơi bày và chiếc còng số tám tra vào tay kẻ ác",
                    "Cảnh sát áp giải Thẩm Minh Viễn và Triệu Bích Nguyệt",
                    "scene", 680,
                    """Người Kể Chuyện: Một đoàn người uy dũng bước vào. Đi đầu là Lục Cảnh Thâm trong bộ vest xám lịch lãm, thần thái ngút ngàn, tay nắm chặt lấy bàn tay nhỏ bé của Thẩm Nhược Hy trong tà váy ngọc bích kiêu sa. Theo sau họ là đội ngũ luật sư hàng đầu thế giới cùng các điều tra viên cao cấp của Cục An ninh Kinh tế Bộ Công an.
Lục Cảnh Thâm: "Triệu tiểu thư và ông Thẩm ăn mừng hơi sớm rồi đấy."
Người Kể Chuyện: Cảnh Thâm khẽ phất tay. Màn hình LED khổng lồ của hội nghị lập tức chiếu đoạn video bằng chứng sắc nét: Chính Triệu Bích Nguyệt đã chi hai mươi tỷ mua chuộc người giúp việc cài thiết bị sao chép dữ liệu mini vào đế đèn bàn trong thư phòng của Cảnh Thâm. Việc Nhược Hy vào mang trà chỉ là cái cớ bị họ cắt ghép tinh vi. Chưa dừng lại ở đó, Cảnh Thâm lạnh lùng tuyên bố: Bản thiết kế bị rò rỉ thực chất là một bản kế hoạch mồi nhử chứa lỗi sai số do chính anh cố tình giăng bẫy từ ba tháng trước để dụ toàn bộ phe cánh phản bội lộ diện!
Lục Cảnh Thâm: "Thẩm Minh Viễn! Toàn bộ chứng cứ ông biển thủ công quỹ, hối lộ quan chức và lập quỹ đen đã được gửi tới Viện Kiểm sát! Còn Triệu Thị, lệnh phong tỏa tài sản và khởi kiện gián điệp kinh tế trị giá hai nghìn tỷ vừa được Tòa án phê chuẩn mười phút trước!" """
                ),
                (
                    "Lời Tuyên Bố Vảy Ngược",
                    "Bảo vệ người phụ nữ của mình trước toàn bộ truyền thông",
                    "Cảnh Thâm nắm chặt tay Nhược Hy trước ánh đèn flash",
                    "character", 1260,
                    """Người Kể Chuyện: Tiếng còi xe cảnh sát hú vang dội bên ngoài sảnh hội nghị. Các chiến sĩ công an bước vào, chiếc còng số tám lạnh ngắt tra thẳng vào tay Thẩm Minh Viễn và Triệu Bích Nguyệt trong tiếng gào khóc thảm thiết và sự bàng hoàng của hàng trăm phóng viên. Triệu Bích Nguyệt ngã quỵ xuống sàn nhà, sự nghiệp và danh vọng tan thành mây khói. Trước hàng trăm ống kính máy quay đang chớp nháy liên tục, Lục Cảnh Thâm kéo Nhược Hy vào lòng, ôm chặt lấy bờ vai cô. Anh đối diện thẳng với truyền thông cả nước, cất giọng nói dõng dạc đầy kiêu hãnh và tình yêu thương sâu sắc:
Lục Cảnh Thâm: "Xin tất cả các vị có mặt ở đây hãy nghe cho rõ: Thẩm Nhược Hy không phải là điểm yếu của Lục Cảnh Thâm này. Cô ấy là vảy ngược bất khả xâm phạm của tôi! Bất cứ kẻ nào dám động đến cô ấy, Lục Thị sẽ khiến kẻ đó không còn chốn dung thân trên cõi đời này!"
Người Kể Chuyện: Nhược Hy ngước nhìn người đàn ông bên cạnh. Trong khoảnh khắc ấy, mọi tủi hờn, uất ức và hoài nghi suốt những ngày qua hoàn toàn tan biến, chỉ còn lại sự ấm áp mãnh liệt từ bàn tay anh đang sưởi ấm tâm hồn cô."""
                )
            ]
        ),

        # CHƯƠNG 7
        (
            "CHƯƠNG VII: BÍ MẬT MƯỜI NĂM TRƯỚC",
            [
                (
                    "Chiếc Hộp Gỗ Cẩn Xà Cừ",
                    "Kỷ vật thời thơ ấu được cất giấu như sinh mạng",
                    "Chiếc khăn len đỏ và móc khóa hoa hướng dương",
                    "concept", 100,
                    """Người Kể Chuyện: Sau chiến thắng vang dội trên thương trường, dự án Cảng Năng lượng Xanh chính thức khởi công, mang lại vị thế độc tôn cho Lục Thị. Danh tiếng của Nhược Hy được minh oan trọn vẹn, công ty Thẩm gia cũng được khôi phục lại quyền sở hữu hợp pháp. Một buổi chiều cuối thu dịu nắng, Lục Lão phu nhân cho mời riêng Nhược Hy đến phòng trà tĩnh mịch tại hậu viện Ngự Cảnh Uyển. Hương trầm thoang thoảng quyện cùng tiếng chim hót ngoài hiên tạo nên không gian yên bình hiếm hoi.
Lục Lão Phu Nhân: "Nhược Hy, con gái ngoan... Bà nội phải thay mặt cả gia tộc này cảm ơn con. Mười năm nay, thằng bé Cảnh Thâm sống như một bóng ma cô độc trong nhà tù tăm tối do chính nó tạo ra. Kể từ ngày con bước chân vào ngôi nhà này, bà mới thấy lại nụ cười và ánh sáng trong đôi mắt của đứa cháu trai đáng thương của bà."
Thẩm Nhược Hy: "Bà nội... con và anh ấy... thực ra chỉ là thực hiện nghĩa vụ theo bản hợp đồng..."
Lục Lão Phu Nhân: "Hợp đồng có thể lừa được thiên hạ ngoài kia, nhưng làm sao che mắt được một bà già đã sống gần một thế kỷ này hả con? Con có biết vì sao ngay lần đầu tiên nhìn thấy bức ảnh của con do Giang Thừa đem về, Cảnh Thâm đã lập tức gật đầu đồng ý ký hợp đồng không?" """
                ),
                (
                    "Ký Ức Đêm Bão Tuyết",
                    "Cô bé quàng khăn len đỏ cứu rỗi linh hồn cậu thiếu niên",
                    "Ký ức hai đứa trẻ sưởi ấm cho nhau giữa bão tuyết",
                    "scene", 680,
                    """Người Kể Chuyện: Nhược Hy ngỡ ngàng ngước nhìn. Lão phu nhân chậm rãi mở chiếc hộp gỗ cẩn xà cừ cổ kính đặt trên bàn trà, lấy ra một chiếc khăn len màu đỏ đã sờn cũ cùng một chiếc móc khóa hình hoa hướng dương bằng gỗ nhỏ xíu. Nhìn thấy hai món đồ ấy, Nhược Hy bàng hoàng đến mức nín thở, tim đập thình thịch liên hồi. Đó chính là chiếc khăn len và chiếc móc khóa do chính tay cô đan và khắc khi mới mười bốn tuổi!
Lục Lão Phu Nhân: "Mười năm trước, vụ tai nạn thảm khốc trên con đèo tuyết ngoại ô đã cướp đi sinh mạng của cha mẹ Cảnh Thâm. Thằng bé bị thương nặng, kẹt sâu dưới rãnh tuyết suốt bảy tiếng đồng hồ trong bóng tối rét buốt cùng thi thể của cha mẹ nó. Nó đã gần như tuyệt vọng và muốn buông xuôi chờ chết... Cho đến khi có một cô bé mười bốn tuổi theo đoàn từ thiện đi ngang qua. Cô bé ấy đã bất chấp nguy hiểm chui xuống hốc tuyết, cởi chiếc khăn len đỏ quàng cho nó, chia cho nó nửa chiếc bánh mì nóng, nắm chặt bàn tay lạnh ngắt của nó suốt ba tiếng đồng hồ và hát khúc hát ru để giữ cho nó không chìm vào cơn hôn mê tử thần..."
Người Kể Chuyện: Ký ức tuổi thơ xa xăm như những thước phim quay chậm ùa về trong tâm trí Nhược Hy. Cô bé năm ấy đã nói với cậu thiếu niên đang tuyệt vọng: Đừng sợ nhé, ánh mặt trời sắp lên rồi. Cậu nhất định phải sống thật kiên cường nhé!"""
                ),
                (
                    "Chân Tướng Mười Năm Chờ Đợi",
                    "Tình yêu âm thầm và sự bảo bọc sâu sắc nhất trần đời",
                    "Nhược Hy ôm chiếc khăn len đỏ khóc nghẹn ngào",
                    "character", 1260,
                    """Lục Lão Phu Nhân: "Sau khi được cứu sống, Cảnh Thâm giữ chiếc khăn len này như sinh mạng. Nó đã cho người lùng sục tìm kiếm cô bé năm ấy suốt mười năm trời ròng rã... Đêm mưa ba tháng trước, khi tay con chạm vào nó, mùi hương hoa nhài và vết bớt nhỏ nơi cổ tay con đã khiến nó nhận ra con ngay lập tức. Thằng bé không hề dùng tiền để mua chuộc con, nó dùng bản hợp đồng một trăm tỷ vì sợ con từ chối, sợ làm con hoảng sợ. Nó đang dùng tất cả những gì mình có để bảo bọc và bù đắp cho ân nhân duy nhất đã cứu rỗi linh hồn nó cả đời này!"
Người Kể Chuyện: Từng giọt nước mắt nóng hổi lăn dài trên má Nhược Hy, rơi xuống làm ướt đẫm chiếc khăn len kỷ vật thời thơ ấu. Cô nghẹn ngào ôm chiếc khăn vào lòng. Thì ra cuộc gặp gỡ dưới mưa đêm không phải là sự tình cờ. Thì ra sự xuất hiện của cô trong cuộc đời anh là định mệnh đã được an bài từ mười năm trước giữa bão tuyết. Người đàn ông luôn tỏ ra lạnh lùng cay nghiệt ấy, thực chất đã khắc sâu bóng hình cô vào tận đáy tim suốt một thập kỷ qua bằng một tình yêu sâu sắc và trầm mặc nhất trần đời."""
                )
            ]
        ),

        # CHƯƠNG 8
        (
            "CHƯƠNG VIII: NGÀY HỢP ĐỒNG HẾT HẠN",
            [
                (
                    "Chiếc Vali Cũ Kỹ",
                    "Ba trăm sáu mươi lăm ngày trôi qua và nỗi buồn ly biệt",
                    "Nhược Hy kéo khóa chiếc vali chuẩn bị rời đi",
                    "character", 100,
                    """Người Kể Chuyện: Thời gian như thoi đưa, ba trăm sáu mươi lăm ngày của bản hợp đồng hôn nhân chiến lược đã chính thức đến ngày kết thúc. Bệnh tình của cha Nhược Hy bình phục một cách thần kỳ nhờ đội ngũ chuyên gia y tế hàng đầu do Cảnh Thâm mời về. Ông đã có thể tự đi lại, tái thiết lại nhà máy dược phẩm gia truyền Thẩm Thị khang trang hơn xưa. Món nợ hai mươi tỷ đã xóa sạch hoàn toàn, và một trăm tỷ thù lao hợp đồng đã được chuyển vào tài khoản cá nhân của Nhược Hy không thiếu một xu. Mọi cam kết trên giấy tờ đã hoàn thành trọn vẹn. Đêm cuối cùng tại Ngự Cảnh Uyển, căn biệt thự chìm trong tĩnh mịch lạ thường. Nhược Hy lặng lẽ xếp từng món đồ cá nhân vào chiếc vali cũ kỹ mà cô đã mang đến vào ngày đầu tiên. Cô không mang theo bất kỳ bộ váy hàng hiệu hay món trang sức đắt tiền nào mà Cảnh Thâm đã mua cho cô trong suốt một năm qua.
Thẩm Nhược Hy: "Một trăm tỷ đã nhận đủ... Cha đã bình an... Giấc mộng hào môn này, đã đến lúc phải tỉnh lại rồi. Mày không thể tham lam hơn nữa, Thẩm Nhược Hy à..." """
                ),
                (
                    "Lời Từ Biệt Cay Đắng",
                    "Khoảng cách vô hình ngăn cách hai trái tim yêu nhau",
                    "Cảnh Thâm và Nhược Hy đứng đối diện trong bóng tối",
                    "character", 680,
                    """Người Kể Chuyện: Cánh cửa phòng ngủ khẽ đẩy mở. Lục Cảnh Thâm đứng tựa lưng vào khung cửa, trên người vẫn là bộ âu phục làm việc quen thuộc. Ánh mắt anh tối sầm lại khi nhìn thấy chiếc vali đã đóng chặt bên chân cô.
Lục Cảnh Thâm: "Cô thu dọn hành lý nhanh nhỉ. Ngày mai mới chính thức hết hạn hợp đồng cơ mà."
Thẩm Nhược Hy: "Sớm muộn gì cũng phải đi, tôi về nhà chăm sóc cha sớm một ngày sẽ tốt hơn. Cảm ơn Lục tổng suốt một năm qua đã che chở cho gia đình tôi. Bệnh mất ngủ của anh dạo này đã khỏi hẳn rồi, sóng não đã hoàn toàn ổn định... Sau này nhớ ăn uống đúng giờ, đừng làm việc thâu đêm nữa nhé."
Lục Cảnh Thâm: "Thẩm Nhược Hy... một năm qua bên nhau... với cô thực sự chỉ là một thương vụ làm ăn sòng phẳng thôi sao? Cô không hề có chút lưu luyến nào với căn nhà này... hay với tôi sao?"
Thẩm Nhược Hy: "Trong hợp đồng... điều khoản thứ tư ghi rất rõ: Tuyệt đối không được nảy sinh tình cảm thật. Tôi chỉ làm đúng theo những gì chúng ta đã cam kết. Chúc Lục tổng sau này tìm được một người môn đăng hộ đối, thật lòng yêu thương anh." """
                ),
                (
                    "Nỗi Đau Trong Bóng Tối",
                    "Sự im lặng xé lòng của hai con người bị trói buộc bởi tự trọng",
                    "Bóng lưng cô độc của Lục Cảnh Thâm trong căn phòng quạnh quẽ",
                    "scene", 1260,
                    """Người Kể Chuyện: Lục Cảnh Thâm cười cay đắng một tiếng. Lòng kiêu hãnh của một người đàn ông đứng trên đỉnh cao quyền lực khiến anh không thể hạ mình van xin cô ở lại. Anh quay lưng bước đi, để lại một câu nói lạnh lùng buốt giá trước khi cánh cửa khép lại:
Lục Cảnh Thâm: "Tốt lắm. Vậy sáng mai tôi sẽ cho xe đưa cô về Thẩm gia. Kể từ nay về sau, hai chúng ta không ai nợ ai!"
Người Kể Chuyện: Tiếng bước chân anh xa dần trên hành lang dài vắng lặng. Khi cánh cửa phòng khép lại, Nhược Hy gục đầu xuống chiếc vali, những giọt nước mắt kìm nén bấy lâu vỡ òa tuôn rơi không dứt. Cô yêu anh. Cô đã yêu người đàn ông cô độc ấy từ lúc nào không hay. Nhưng cô sợ thân phận chênh lệch, sợ mình chỉ là cái bóng thay thế cho cô bé năm xưa, sợ rằng tình yêu của một thiên kim sa cơ sẽ trở thành gánh nặng cản trở tiền đồ rực rỡ của anh. Đêm hôm đó, cả hai con người đều thức trắng trong nỗi đau đớn xé nát tâm can."""
                )
            ]
        ),

        # CHƯƠNG 9
        (
            "CHƯƠNG IX: BẢN HỢP ĐỒNG TRỌN ĐỜI",
            [
                (
                    "Cuộc Đua Về Phi Trường",
                    "Sự hoảng loạn của tổng tài khi sắp mất đi người mình yêu nhất",
                    "Chiếc xe Maybach lao vun vút trên đại lộ hướng về sân bay",
                    "scene", 100,
                    """Người Kể Chuyện: Tám giờ sáng hôm sau, bầu trời thành phố trong xanh rực rỡ sau chuỗi ngày mưa kéo dài. Tại Sân bay Quốc tế, Thẩm Nhược Hy cầm trên tay chiếc vé máy bay chuẩn bị cùng cha lên chuyến bay sang Thụy Sĩ dưỡng bệnh dài hạn. Cô muốn rời khỏi thành phố đầy ắp kỷ niệm đau thương này để bắt đầu một cuộc đời mới. Cùng lúc đó, tại văn phòng Chủ tịch tầng sáu mươi tám Tập đoàn Lục Thị, Cảnh Thâm ngồi bất động trước bàn làm việc, tách cà phê đã nguội ngắt từ lâu. Trước mặt anh là bản hợp đồng hôn nhân một năm đã hoàn tất. Trợ lý Giang Thừa hớt hải đạp cửa xông vào, gương mặt tái mét không kịp gõ cửa:
Trợ Lý Giang: "Lục tổng! Nguy rồi! Thẩm tiểu thư không về Thẩm gia, cô ấy đang làm thủ tục tại sân bay quốc tế để bay sang châu Âu cùng Thẩm lão gia! Chuyến bay VN-720 sẽ cất cánh sau đúng ba mươi phút nữa!"
Người Kể Chuyện: Chiếc bút máy mạ vàng trên tay Lục Cảnh Thâm rơi choảng xuống sàn gạch. Tất cả sự điềm tĩnh, lạnh lùng và kiêu ngạo mà anh xây dựng suốt hai mươi chín năm qua sụp đổ hoàn toàn trong tích tắc. Nỗi sợ hãi mất đi cô gái ấy một lần nữa như mười năm trước bóp nghẹt lồng ngực anh.
Lục Cảnh Thâm: "Chuẩn bị xe ngay! Thông báo cho Cục Hàng không, bằng mọi giá phải hoãn chuyến bay đó lại cho tôi!"
Người Kể Chuyện: Chiếc Maybach của Lục Cảnh Thâm gầm rú xé gió trên đại lộ, vượt qua mọi đèn đỏ lao thẳng về phía sân bay như một mũi tên xé toạc không gian."""
                ),
                (
                    "Xé Nát Bản Hợp Đồng Bạc Tỷ",
                    "Lời tỏ tình chấn động giữa hàng ngàn hành khách sân bay",
                    "Cảnh Thâm xé nát tờ hợp đồng giữa sảnh sân bay",
                    "concept", 680,
                    """Người Kể Chuyện: Tại sảnh chờ sân bay quốc tế, hành khách đang bắt đầu xếp hàng qua cửa an ninh soát vé. Nhược Hy kéo vali, ngoảnh đầu nhìn lại thành phố lần cuối, khóe mắt vương ngấn lệ thì thầm lời từ biệt: Tạm biệt Lục Cảnh Thâm, chúc anh một đời bình an... Đột nhiên, cả khu vực sảnh chờ xôn xao náo loạn. Hàng chục vệ sĩ áo đen phong tỏa lối vào cửa kiểm soát. Một bóng dáng cao lớn với chiếc áo sơ mi xộc xệch, cà vạt nới lỏng, mái tóc rối bời vì chạy thục mạng đang điên cuồng lao qua đám đông. Đó là Lục Cảnh Thâm! Người đàn ông luôn xuất hiện hoàn hảo trên trang bìa các tạp chí tài chính thế giới lúc này không màng đến bất kỳ hình tượng nào, chỉ điên cuồng tìm kiếm một bóng hình. Nhìn thấy Nhược Hy ở cửa an ninh, anh lao tới chộp chặt lấy cánh tay cô, kéo mạnh cô vào lòng siết chặt như muốn hòa cô vào da thịt mình.
Lục Cảnh Thâm: "Em dám đi? Ai cho phép em mang theo trái tim của tôi rời khỏi thành phố này hả?"
Thẩm Nhược Hy: "Cảnh Thâm? Anh làm gì ở đây? Hợp đồng đã kết thúc rồi! Tôi không còn là Lục phu nhân của anh nữa..."
Người Kể Chuyện: Trước ánh mắt chứng kiến của hàng ngàn hành khách ngỡ ngàng, Lục Cảnh Thâm rút từ túi áo ngực ra bản hợp đồng hôn nhân một trăm tỷ. Không một chút do dự, anh dùng hai tay xé toạc tờ hợp đồng ra làm đôi, làm tư, rồi ném những mảnh giấy vụn bay lả tả giữa không trung!
Lục Cảnh Thâm: "Bản hợp đồng chết tiệt này kết thúc rồi! Nhược Hy, mười năm trước em cứu mạng tôi dưới trời tuyết, tôi đã thề cả đời này chỉ cưới một mình em! Tôi không cần một cô vợ hợp đồng ngoan ngoãn. Tôi cần Thẩm Nhược Hy làm người vợ thật sự của Lục Cảnh Thâm này! Một trăm tỷ đó là sính lễ của anh, toàn bộ tài sản Lục Thị là của em, mạng sống của anh cũng là của em!" """
                ),
                (
                    "Bản Giao Ước Trọn Đời Trọn Kiếp",
                    "Chiếc nhẫn hoa hướng dương và cái kết viên mãn hạnh phúc",
                    "Cảnh Thâm cầu hôn Nhược Hy trước sự chúc phúc của mọi người",
                    "scene", 1260,
                    """Người Kể Chuyện: Nhược Hy che miệng khóc nấc lên từng tiếng, xúc động không thốt nên lời. Cảnh Thâm quỳ một chân xuống sàn gạch sân bay, rút ra chiếc hộp nhung đỏ chứa chiếc nhẫn kim cương hồng hình hoa hướng dương độc bản lấp lánh dưới ánh mặt trời rực rỡ.
Lục Cảnh Thâm: "Không có em, bóng đêm của anh sẽ không bao giờ có bình minh. Lấy anh nhé? Không phải vì một bản hợp đồng một năm, mà là một bản giao ước trọn đời trọn kiếp!"
Thẩm Nhược Hy: "Em đồng ý! Cảnh Thâm, em yêu anh!"
Người Kể Chuyện: Tiếng vỗ tay hoan hô, reo hò chúc phúc vang dội khắp cả phi trường quốc tế. Cha của Nhược Hy đứng phía sau mỉm cười gật đầu rưng rưng mãn nguyện. Lục Cảnh Thâm ôm bổng Nhược Hy lên giữa không trung rồi đặt lên môi cô một nụ hôn nồng nàn, say đắm dưới ánh nắng mai rực rỡ xuyên qua mái vòm kính. Bản hợp đồng một trăm tỷ đã tan thành mây khói, nhưng một bản giao ước tình yêu vĩnh cửu vừa được viết nên bằng sự chân thành và định mệnh mười năm. Từ đây về sau, giữa thế gian phồn hoa rộng lớn, vị tổng tài bạc tỷ đã tìm thấy ánh trăng dịu êm của riêng mình – người sẽ cùng anh đi qua mọi giông bão cuộc đời, vẽ nên những ngày tháng bình yên và hạnh phúc trọn vẹn."""
                )
            ]
        )
    ]

    beat_idx = 1
    beats = []
    for ch_title, ch_beats in chapters:
        for headline, subhead, label, b_type, pos_x, raw_text in ch_beats:
            beats.append({
                "id": f"beat_{beat_idx:02d}",
                "role": f"scene_{(beat_idx-1)//3 + 1:02d}_part_{(beat_idx-1)%3 + 1}",
                "rawText": raw_text.strip(),
                "visual": {
                    "headline": headline,
                    "subhead": subhead,
                    "badge": ch_title,
                    "label": label,
                    "type": b_type,
                    "region": {
                        "x": pos_x,
                        "y": 80,
                        "width": 550,
                        "height": 920
                    }
                }
            })
            beat_idx += 1

    job_data = {
        "jobId": "job-hop-dong-100-ty-tong-tai",
        "title": "Bản Hợp Đồng 100 Tỷ: Ánh Trăng Của Tổng Tài Bạc Tỷ (Bản Full 60 Phút)",
        "workshop": "whiteboard",
        "archetype": "storytelling",
        "targetPlatform": "youtube_long",
        "canvas": {
            "width": 1920,
            "height": 1080,
            "fps": 90
        },
        "voice": {
            "provider": "edge-tts",
            "voiceId": "vi-VN-NamMinhNeural",
            "speed": 0.85,
            "rate": "-16%",
            "pitch": "+0Hz",
            "volume": "+0%"
        },
        "metadata": {
            "genre": "Ngôn tình đô thị, Tổng tài lạnh lùng, Cưới trước yêu sau, Chữa lành, Hào môn thế gia, Sủng ngọt, HE",
            "durationExpectedMinutes": 60,
            "author": "Omni-Director",
            "characters": [
                "Lục Cảnh Thâm (29 tuổi, Chủ tịch Lục Thị, mất ngủ kinh niên, lạnh lùng quyết đoán)",
                "Thẩm Nhược Hy (24 tuổi, Thiên kim sa cơ, thông minh kiên cường, đôi mắt sáng)",
                "Lục Lão Phu Nhân (75 tuổi, Bà nội Cảnh Thâm, nắm quyền tối cao gia tộc, hiền từ)",
                "Trợ lý Giang Thừa (27 tuổi, Cánh tay phải nhanh nhẹn đắc lực)",
                "Triệu Bích Nguyệt (26 tuổi, Thiên kim đối thủ kiêu kỳ nhiều tâm cơ)",
                "Thẩm Minh Viễn (50 tuổi, Chú ruột tham lam phản bội Thẩm gia)"
            ],
            "characters_voice": {
                "lục cảnh thâm": { "voice": "vi-VN-NamMinhNeural", "rate": "-14%", "pitch": "-5Hz", "volume": "+0%" },
                "cảnh thâm": { "voice": "vi-VN-NamMinhNeural", "rate": "-14%", "pitch": "-5Hz", "volume": "+0%" },
                "thẩm nhược hy": { "voice": "vi-VN-HoaiMyNeural", "rate": "-14%", "pitch": "+0Hz", "volume": "+0%" },
                "nhược hy": { "voice": "vi-VN-HoaiMyNeural", "rate": "-14%", "pitch": "+0Hz", "volume": "+0%" },
                "lục lão phu nhân": { "voice": "vi-VN-HoaiMyNeural", "rate": "-18%", "pitch": "-3Hz", "volume": "+0%" },
                "bà nội": { "voice": "vi-VN-HoaiMyNeural", "rate": "-18%", "pitch": "-3Hz", "volume": "+0%" },
                "giang thừa": { "voice": "vi-VN-NamMinhNeural", "rate": "-10%", "pitch": "+3Hz", "volume": "+0%" },
                "trợ lý giang": { "voice": "vi-VN-NamMinhNeural", "rate": "-10%", "pitch": "+3Hz", "volume": "+0%" },
                "triệu bích nguyệt": { "voice": "vi-VN-HoaiMyNeural", "rate": "-12%", "pitch": "+4Hz", "volume": "+0%" },
                "thẩm minh viễn": { "voice": "vi-VN-NamMinhNeural", "rate": "-12%", "pitch": "-3Hz", "volume": "+0%" },
                "người kể chuyện": { "voice": "vi-VN-NamMinhNeural", "rate": "-16%", "pitch": "+0Hz", "volume": "+0%" }
            },
            "tags": [
                "truyenaudio",
                "ngontinh",
                "tongtai",
                "hopdong100ty",
                "sachnoi",
                "cuoitruocyeusau",
                "chualanh",
                "whiteboardstory"
            ]
        },
        "beats": beats
    }

    with open(job_output, "w", encoding="utf-8") as f:
        json.dump(job_data, f, ensure_ascii=False, indent=2)

    total_words = sum(len(b["rawText"].split()) for b in beats)
    print(f"[OK] Đã tạo thành công file: {job_output}")
    print(f"[*] Tổng số beats: {len(beats)}")
    print(f"[*] Tổng số từ thoại: {total_words} từ")

if __name__ == "__main__":
    build_epic_60min()
