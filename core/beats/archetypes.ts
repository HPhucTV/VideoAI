/**
 * OmniVideo Studio - 5 Scriptwriting Archetypes
 * Professional script templates with Retention Engineering and Audio Pacing.
 */

import type { ArchetypeDefinition, BeatArchetype } from "./types.ts";

export const ARCHETYPES: Record<BeatArchetype, ArchetypeDefinition> = {
  // 1. STORYTELLING / DRAMA (Cổ tích, Tự sự, Câu chuyện bài học)
  storytelling: {
    id: "storytelling",
    name: "Storytelling & Cổ Tích / Drama",
    description: "Cấu trúc vòng tròn tự sự (Dan Harmon Story Circle). Thích hợp cho video kể chuyện, hoạt hình bảng trắng, case study nhân vật.",
    targetPlatform: "both",
    recommendedDurationSec: { min: 45, ideal: 60, max: 120 },
    beatRoles: [
      {
        role: "exposition",
        name: "Khởi Đầu Bình Yên",
        purpose: "Thiết lập bối cảnh và giới thiệu nhân vật chính trong trạng thái quen thuộc.",
        idealPercent: "0% - 15%",
        retentionTip: "Gieo ngay một hạt mầm mâu thuẫn ngầm trong câu đầu tiên."
      },
      {
        role: "inciting_incident",
        name: "Biến Cố Khởi Nguồn",
        purpose: "Sự cố xảy ra phá vỡ sự bình yên, đặt nhân vật vào thử thách cam go.",
        idealPercent: "15% - 30%",
        retentionTip: "Tạo cảm xúc đồng cảm hoặc bức xúc thay cho nhân vật."
      },
      {
        role: "rising_conflict",
        name: "Xung Đột Leo Thang",
        purpose: "Nhân vật nỗ lực vượt qua nhưng liên tục gặp rào cản và áp bức lớn hơn.",
        idealPercent: "30% - 50%",
        retentionTip: "Sử dụng SFX kịch tính (dramatic_boom) và đẩy nhịp đọc nhanh hơn +5%."
      },
      {
        role: "rehook_crisis",
        name: "Điểm Tái Kích Thích (Mid-Rehook)",
        purpose: "Tình huống tưởng chừng bế tắc hoàn toàn, câu hỏi mở khơi dậy tò mò đỉnh điểm.",
        idealPercent: "50% - 65%",
        retentionTip: "Chèn câu lật: 'Nhưng đúng lúc tuyệt vọng nhất...' để giữ khán giả không lướt qua."
      },
      {
        role: "climax",
        name: "Đỉnh Điểm & Hóa Giải",
        purpose: "Hành động quyết định hoặc phép màu chính nghĩa xuất hiện, lật ngược tình thế.",
        idealPercent: "65% - 85%",
        retentionTip: "Visual zoom punch, nhịp điệu hào hùng, chiến thắng thỏa mãn."
      },
      {
        role: "resolution_moral",
        name: "Kết Thúc & Bài Học Nhân Quả",
        purpose: "Trật tự mới được lập lại, đúc kết chân lý sâu sắc lay động người xem.",
        idealPercent: "85% - 100%",
        retentionTip: "Giọng đọc chậm lại -5%, ấm áp, kêu gọi chia sẻ cảm nghĩ."
      }
    ]
  },

  // 2. EXPLAINER / TECH (Giải thích công nghệ & Khái niệm)
  explainer: {
    id: "explainer",
    name: "Tech Explainer / Micro-Learning",
    description: "Khung PAS nâng cao (Problem - Agitate - Solve - Proof). Chuẩn hóa cho video TikTok 50s-60s giải thích công nghệ, kinh doanh.",
    targetPlatform: "tiktok",
    recommendedDurationSec: { min: 30, ideal: 45, max: 60 },
    beatRoles: [
      {
        role: "hook",
        name: "Hook Gây Chú Ý & Tranh Cãi",
        purpose: "Đưa ra câu hỏi hóc búa hoặc sự thật phản trực giác trong 3 giây đầu.",
        idealPercent: "0% - 12%",
        retentionTip: "Tuyệt đối không chào hỏi. Vào thẳng: 'Bạn có biết tại sao 90% kỹ sư...'"
      },
      {
        role: "problem",
        name: "Đau Điểm Cốt Lõi (The Pain)",
        purpose: "Mô tả vấn đề nhức nhối khi không áp dụng công nghệ/kiến thức này.",
        idealPercent: "12% - 28%",
        retentionTip: "Dùng từ ngữ gợi hình: nghẽn cổ chai, sập server, đốt tiền."
      },
      {
        role: "solution",
        name: "Giải Pháp Lõi (The Hero)",
        purpose: "Giới thiệu công nghệ/khái niệm như một giải pháp cứu cánh bất ngờ.",
        idealPercent: "28% - 48%",
        retentionTip: "SFX ding_idea hoặc whoosh_impact, hiển thị Big Number hoặc Core Keyword."
      },
      {
        role: "rehook_deepdive",
        name: "Re-hook & Cơ Chế Hoạt Động",
        purpose: "Hâm nóng sự chú ý và giải thích ngắn gọn nguyên lý vận hành bên trong.",
        idealPercent: "48% - 70%",
        retentionTip: "Chèn câu nối: 'Nhưng bí mật thực sự nằm ở chỗ này...'"
      },
      {
        role: "impact_proof",
        name: "Bằng Chứng & Kết Quả Định Lượng",
        purpose: "Chứng minh hiệu quả bằng con số ấn tượng (gấp 10x, tiết kiệm 80%).",
        idealPercent: "70% - 88%",
        retentionTip: "Hiển thị so sánh Before/After trực quan."
      },
      {
        role: "cta",
        name: "Đúc Kết & Call To Action",
        purpose: "Tóm gọn trong 1 câu và kêu gọi follow kênh để đón xem video sau.",
        idealPercent: "88% - 100%",
        retentionTip: "Lời kêu gọi tự nhiên, gắn với lợi ích nhận thêm tài liệu hoặc mẹo hay."
      }
    ]
  },

  // 3. VERSUS BATTLE (So sánh đối đầu A vs B)
  versus: {
    id: "versus",
    name: "Versus Battle (A vs B)",
    description: "So sánh đối đầu gay cấn: MySQL vs Redis, React vs Vue, iPhone vs Samsung.",
    targetPlatform: "both",
    recommendedDurationSec: { min: 40, ideal: 55, max: 75 },
    beatRoles: [
      {
        role: "dilemma_hook",
        name: "Thế Tiến Thoái Lưỡng Nan",
        purpose: "Đặt 2 đối thủ lên bàn cân và nêu nghịch lý khiến người xem đau đầu chọn lựa.",
        idealPercent: "0% - 15%",
        retentionTip: "Hỏi ngay: 'Nên chọn A hay B khi bắt đầu dự án năm nay?'"
      },
      {
        role: "contender_a",
        name: "Thế Mạnh Vũ Bão Của Phe A",
        purpose: "Trình diễn điểm mạnh vượt trội và trường hợp sử dụng lý tưởng của A.",
        idealPercent: "15% - 35%",
        retentionTip: "Nhịp điệu dứt khoát, liệt kê 2 ưu điểm đắt giá nhất."
      },
      {
        role: "contender_b",
        name: "Đòn Phản Công Của Phe B",
        purpose: "Chỉ ra điểm yếu chí tử của A và cách B đè bẹp đối thủ ở sân chơi khác.",
        idealPercent: "35% - 55%",
        retentionTip: "SFX glitch_error ở A và ding_idea ở B, kích thích tranh luận."
      },
      {
        role: "twist_rehook",
        name: "Re-hook: Đánh Đổi Lớn (Trade-off)",
        purpose: "Nhấn mạnh không có giải pháp nào hoàn hảo, chỉ có sự đánh đổi.",
        idealPercent: "55% - 72%",
        retentionTip: "'Nhưng 90% người mới đều mắc sai lầm chí mạng ở bước này...'"
      },
      {
        role: "final_verdict",
        name: "Phán Quyết Thực Chiến",
        purpose: "Công thức quyết định rõ ràng: Khi nào bắt buộc dùng A, khi nào dùng B.",
        idealPercent: "72% - 90%",
        retentionTip: "Đưa ra bảng chốt hạ 2 dòng siêu ngắn gọn, dễ nhớ."
      },
      {
        role: "cta_debate",
        name: "Kêu Gọi Tranh Luận Comment",
        purpose: "Hỏi khán giả: 'Dự án của bạn đang dùng phe nào? Để lại bình luận bên dưới.'",
        idealPercent: "90% - 100%",
        retentionTip: "Tăng mạnh engagement qua bình luận cọ xát ý kiến."
      }
    ]
  },

  // 4. MYTHBUSTER (Lật tẩy lầm tưởng / Phá vỡ định kiến)
  mythbuster: {
    id: "mythbuster",
    name: "Mythbuster (Lật Tẩy Sai Lầm)",
    description: "Đánh trúng tâm lý 'tưởng vậy mà không phải vậy', kích thích người xem xem đến cùng để kiểm chứng.",
    targetPlatform: "tiktok",
    recommendedDurationSec: { min: 35, ideal: 50, max: 65 },
    beatRoles: [
      {
        role: "myth_hook",
        name: "Nêu Bật Lầm Tưởng Phổ Biến",
        purpose: "Nêu một niềm tin mà hầu như ai cũng tưởng là đúng, rồi khẳng định: 'Hoàn toàn sai!'",
        idealPercent: "0% - 15%",
        retentionTip: "Từ khóa hapticText màu đỏ cảnh báo, SFX glitch_error."
      },
      {
        role: "common_mistake",
        name: "Cái Giá Phải Trả Khi Tin Lầm",
        purpose: "Chỉ ra những hệ quả tai hại khi làm theo cách truyền miệng sai lầm đó.",
        idealPercent: "15% - 35%",
        retentionTip: "Tạo cảm giác 'giật mình' nhận ra bản thân từng mắc phải."
      },
      {
        role: "shocking_truth",
        name: "Sự Thật Bất Ngờ (The Twist)",
        purpose: "Bật mí sự thật khoa học / kỹ thuật thực sự đằng sau vấn đề.",
        idealPercent: "35% - 55%",
        retentionTip: "Camera zoom punch, SFX dramatic_boom, giải thích ngắn trong 1 câu."
      },
      {
        role: "evidence_breakdown",
        name: "Giải Mã & Chứng Minh Thực Tế",
        purpose: "Đưa ra dẫn chứng thực tế hoặc benchmark không thể chối cãi.",
        idealPercent: "55% - 75%",
        retentionTip: "Re-hook nhẹ: 'Tại sao lại như vậy? Hãy nhìn vào cách bộ nhớ xử lý...'"
      },
      {
        role: "actionable_rule",
        name: "Quy Tắc Hành Động Đúng",
        purpose: "Quy tắc 1-2-3 thực chiến để người xem áp dụng sửa sai ngay lập tức.",
        idealPercent: "75% - 90%",
        retentionTip: "Rõ ràng, đơn giản, có thể lưu video lại xem khi cần."
      },
      {
        role: "share_cta",
        name: "Kêu Gọi Lưu & Chia Sẻ",
        purpose: "'Lưu video này lại trước khi bạn hoặc đồng nghiệp lặp lại sai lầm đó!'",
        idealPercent: "90% - 100%",
        retentionTip: "Kích hoạt hành vi Save (Lưu) và Share (Chia sẻ) của thuật toán TikTok."
      }
    ]
  },

  // 5. BREAKING NEWS (Tin tức nóng & Cập nhật thời sự)
  news: {
    id: "news",
    name: "Breaking News & Thời Sự Nóng",
    description: "Mô hình kim tự tháp ngược (Inverted Pyramid). Dành cho video thời sự nóng, cập nhật công nghệ AI, bản tin vắn.",
    targetPlatform: "both",
    recommendedDurationSec: { min: 30, ideal: 40, max: 60 },
    beatRoles: [
      {
        role: "breaking_hook",
        name: "Tiêu Điểm Nóng (Breaking Headline)",
        purpose: "Tuyên bố sự kiện lớn vừa xảy ra với giọng điệu khẩn trương, thời sự.",
        idealPercent: "0% - 15%",
        retentionTip: "Tông giọng dồn dập +5%, badge 'BREAKING NEWS' nhấp nháy."
      },
      {
        role: "key_facts",
        name: "Dữ Liệu & Điểm Mấu Chốt",
        purpose: "3 gạch đầu dòng then chốt về sự kiện: Ai, Cái gì, Ở đâu, Khi nào.",
        idealPercent: "15% - 40%",
        retentionTip: "Thông tin gãy gọn, không dài dòng, con số rõ ràng."
      },
      {
        role: "context_analysis",
        name: "Bối Cảnh & Tác Động Rộng Lớn",
        purpose: "Giải thích vì sao sự kiện này quan trọng và ảnh hưởng đến người xem ra sao.",
        idealPercent: "40% - 60%",
        retentionTip: "Re-hook: 'Động thái này đe dọa trực tiếp đến thị phần của...'"
      },
      {
        role: "rehook_reaction",
        name: "Phản Ứng Cộng Đồng & Chuyên Gia",
        purpose: "Các ý kiến trái chiều hoặc phản ứng mạnh mẽ từ các bên liên quan.",
        idealPercent: "60% - 80%",
        retentionTip: "Tạo cảm giác hồi hộp chờ xem diễn biến tiếp theo."
      },
      {
        role: "future_outlook",
        name: "Dự Báo & Góc Nhìn Tiếp Theo",
        purpose: "Điều gì sẽ diễn ra trong vài ngày/tuần tới, người xem cần chuẩn bị gì.",
        idealPercent: "80% - 92%",
        retentionTip: "Đưa ra nhận định sắc sảo, gợi mở tương lai."
      },
      {
        role: "discussion_cta",
        name: "Kêu Gọi Thảo Luận Thời Sự",
        purpose: "Hỏi quan điểm của người xem về sự kiện để bùng nổ thảo luận.",
        idealPercent: "92% - 100%",
        retentionTip: "Ví dụ: 'Bạn đánh giá thế nào về bước đi này? Thảo luận bên dưới nhé!'"
      }
    ]
  },

  // 6. CINEMATIC 3D / DONGHUA (Phim hoạt hình 3D & Tiên hiệp chuẩn điện ảnh)
  cinematic: {
    id: "cinematic",
    name: "Cinematic 3D / Donghua Điện Ảnh",
    description: "Cấu trúc 5 Hồi điện ảnh tiêu chuẩn Hollywood/Donghua (45-60 shots/5 phút, ASL 4.0-7.0s, 100% Gen V AI video, Zero-Loop Mandate).",
    targetPlatform: "both",
    recommendedDurationSec: { min: 60, ideal: 300, max: 600 },
    beatRoles: [
      {
        role: "act_1_establishment",
        name: "Hồi 1: Khởi Đầu & Mâu Thuẫn Ngầm",
        purpose: "Establishing shot bối cảnh 4K, giới thiệu nhân vật chính và mâu thuẫn ngầm đe dọa.",
        idealPercent: "0% - 15%",
        retentionTip: "3 giây đầu gây sốc bằng góc máy đại cảnh hoành tráng hoặc câu tuyên bố chấn động."
      },
      {
        role: "act_2_rising_tension",
        name: "Hồi 2: Thử Thách & Đối Đầu Trực Diện",
        purpose: "Xung đột bùng nổ, đối thoại luân phiên Shot/Reverse-Shot (nhịp thoại vàng <= 20 từ).",
        idealPercent: "15% - 40%",
        retentionTip: "Chuyển góc máy liên tục qua vai (OTS) và cận cảnh phản ứng người nghe."
      },
      {
        role: "act_3_crisis_rehook",
        name: "Hồi 3: Biến Cố Nguy Cấp & Re-hook Đỉnh Điểm",
        purpose: "Tình huống nghìn cân treo sợi tóc, nhân vật rơi vào bẫy tuyệt vọng.",
        idealPercent: "40% - 70%",
        retentionTip: "Kích hoạt tiếng rền trầm Sub-bass drone 48Hz, đặc tả chi tiết ánh mắt hoặc chuôi kiếm."
      },
      {
        role: "act_4_climax_battle",
        name: "Hồi 4: Đại Chiến & Tuyệt Kỹ Quyết Định",
        purpose: "Cao trào bùng nổ, thi triển thần thông võ học, chuyển động camera dồn dập (ASL 3.5s - 5.0s).",
        idealPercent: "70% - 90%",
        retentionTip: "100% video chuyển động Veo 2 sống động, kết hợp âm thanh va chạm Foley uy lực."
      },
      {
        role: "act_5_resolution_loop",
        name: "Hồi 5: Hóa Giải & Vòng Lặp Vận Mệnh",
        purpose: "Hóa giải mâu thuẫn, đúc kết vận mệnh và câu thoại kết nối vòng lặp (The Infinite Loop).",
        idealPercent: "90% - 100%",
        retentionTip: "Câu kết móc nối tự nhiên về câu thoại mở đầu để đạt tỉ lệ Retention > 100%."
      }
    ]
  }
};

export function getArchetypeDefinition(archetype: BeatArchetype): ArchetypeDefinition {
  const found = ARCHETYPES[archetype];
  if (!found) {
    throw new Error(`Archetype khong hop le: '${archetype}'. Cac lua chon: ${Object.keys(ARCHETYPES).join(", ")}`);
  }
  return found;
}
