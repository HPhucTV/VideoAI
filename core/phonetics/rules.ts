/**
 * Vietnamese Phonetics Normalization Rules
 * Context-aware text transformations to ensure Edge TTS & other providers pronounce text correctly.
 */

// Đọc số nguyên tiếng Việt từ 0 đến 999999999999
const chuSo = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"];

function docHangTram(so: number, dayDu: boolean): string {
  let chuoi = "";
  const tram = Math.floor(so / 100);
  const chuc = Math.floor((so % 100) / 10);
  const donvi = so % 10;

  if (dayDu || tram > 0) {
    chuoi += " " + chuSo[tram] + " trăm";
    chuoi += docHangChuc(chuc, donvi, true);
  } else {
    chuoi += docHangChuc(chuc, donvi, false);
  }
  return chuoi;
}

function docHangChuc(chuc: number, donvi: number, dayDu: boolean): string {
  let chuoi = "";
  if (chuc > 1) {
    chuoi += " " + chuSo[chuc] + " mươi";
    if (donvi === 1) chuoi += " mốt";
    else if (donvi === 4) chuoi += " tư";
    else if (donvi === 5) chuoi += " lăm";
    else if (donvi > 0) chuoi += " " + chuSo[donvi];
  } else if (chuc === 1) {
    chuoi += " mười";
    if (donvi === 1) chuoi += " một";
    else if (donvi === 5) chuoi += " lăm";
    else if (donvi > 0) chuoi += " " + chuSo[donvi];
  } else if (dayDu && donvi > 0) {
    chuoi += " linh " + chuSo[donvi];
  } else if (!dayDu && donvi > 0) {
    chuoi += " " + chuSo[donvi];
  }
  return chuoi;
}

export function readIntegerVN(n: number | string): string {
  const numStr = n.toString().replace(/^0+/, "") || "0";
  if (numStr === "0") return "không";

  let i = numStr.length;
  let blocks: number[] = [];
  while (i > 0) {
    const start = Math.max(0, i - 3);
    blocks.unshift(parseInt(numStr.substring(start, i), 10));
    i = start;
  }

  const donViLop = ["", " nghìn", " triệu", " tỷ", " nghìn tỷ", " triệu tỷ"];
  let res = "";

  for (let idx = 0; idx < blocks.length; idx++) {
    const blockVal = blocks[idx];
    const power = blocks.length - 1 - idx;
    if (blockVal > 0) {
      const dayDu = idx > 0;
      res += docHangTram(blockVal, dayDu) + donViLop[power % 4];
      if (power >= 4 && power % 4 === 0) res += " tỷ";
    }
  }

  return res.trim().replace(/\s+/g, " ");
}

export function normalizeVietnameseText(text: string): string {
  if (!text) return "";
  let out = text;

  // 1. Phân biệt dấu chấm ngăn hàng nghìn VN kèm tiền tệ: 50.000đ, 50.000 đồng, 50.000 VNĐ
  out = out.replace(/(\d{1,3}(?:\.\d{3})+)\s*(?:đ|đồng|vnđ|vnd)(?=\s|$|[.,;!?])/gi, (_, numGroup) => {
    const cleanNum = numGroup.replace(/\./g, "");
    return `${readIntegerVN(cleanNum)} đồng`;
  });

  // 1b. Dấu chấm ngăn hàng nghìn số thường: 1.000.000
  out = out.replace(/\b(\d{1,3}(?:\.\d{3})+)\b/g, (_, numGroup) => {
    const cleanNum = numGroup.replace(/\./g, "");
    return readIntegerVN(cleanNum);
  });

  // 2. Số phiên bản (Version numbers): Đứng sau GPT, iOS, Android, Version, Bản, v.v.
  out = out.replace(/(?:bản|phiên bản|version|v|gpt|ios|android)\s*(\d+)[\.,](\d+)(?:[\.,](\d+))?/gi, (match) => {
    return match.replace(/[\.,]/g, " chấm ");
  });

  // 3. Phần trăm (Percentage): 82.7% -> tám mươi hai phẩy bảy phần trăm
  out = out.replace(/(\d+)[\.,](\d+)%/g, (_, integerPart, decimalPart) => {
    const readInt = readIntegerVN(integerPart);
    const readDec = decimalPart.split("").map((d: string) => chuSo[parseInt(d, 10)]).join(" ");
    return `${readInt} phẩy ${readDec} phần trăm`;
  });
  out = out.replace(/(\d+)%/g, (_, num) => {
    return `${readIntegerVN(num)} phần trăm`;
  });

  // 4. Số thập phân đơn lẻ (3.5 -> ba phẩy năm hoặc ba chấm năm)
  out = out.replace(/\b(\d+)[\.,](\d+)\b/g, (_, integerPart, decimalPart) => {
    // Nếu decimalPart có độ dài khác 3 (không phải hàng nghìn)
    if (decimalPart.length !== 3) {
      const readInt = readIntegerVN(integerPart);
      const readDec = decimalPart.split("").map((d: string) => chuSo[parseInt(d, 10)]).join(" ");
      return `${readInt} chấm ${readDec}`;
    }
    return _;
  });

  // 5. Từ viết tắt công nghệ (Acronyms)
  const acronyms: Record<string, string> = {
    "AI": "ây ai",
    "API": "ây pi ai",
    "UI/UX": "u ai u ích",
    "UI": "u ai",
    "UX": "u ích",
    "RAM": "ram",
    "CPU": "xê pê u",
    "GPU": "gờ pê u",
    "SSD": "ét ét đê",
    "HDD": "hắt đê đê",
    "HTML": "hắt tê em lờ",
    "CSS": "xê ét ét",
    "JS": "giây ét",
    "TS": "tê ét",
    "Docker": "Đốc cơ",
    "Kubernetes": "Cu bơ nét tít",
    "GitHub": "Gít hắp",
    "Git": "Gít",
    "Linux": "Li nớt",
  };

  for (const [key, replacement] of Object.entries(acronyms)) {
    const reg = new RegExp(`\\b${key}\\b`, "g");
    out = out.replace(reg, replacement);
  }

  // 6. Đơn vị kỹ thuật & tiền tệ
  out = out.replace(/\b(\d+)\s*GB\b/gi, (_, n) => `${readIntegerVN(n)} ghi ga bai`);
  out = out.replace(/\b(\d+)\s*MB\b/gi, (_, n) => `${readIntegerVN(n)} mê ga bai`);
  out = out.replace(/\b(\d+)\s*TB\b/gi, (_, n) => `${readIntegerVN(n)} tê ra bai`);
  out = out.replace(/\b(\d+)\s*mAh\b/gi, (_, n) => `${readIntegerVN(n)} miliampe giờ`);
  out = out.replace(/\b(\d+)\s*MP\b/gi, (_, n) => `${readIntegerVN(n)} megapixel`);
  out = out.replace(/\b5G\b/gi, "năm gờ");
  out = out.replace(/\b4G\b/gi, "bốn gờ");
  out = out.replace(/\$(\d+)/g, (_, n) => `${readIntegerVN(n)} đô la`);
  out = out.replace(/(\d+)\s*x\b/gi, (_, n) => (n === "2" ? "gấp đôi" : `gấp ${readIntegerVN(n)} lần`));
  out = out.replace(/(\d+)\s*:\s*(\d+)/g, (_, a, b) => `${readIntegerVN(a)} trên ${readIntegerVN(b)}`);

  // 7. Ký tự biểu tượng đặc biệt
  out = out.replace(/\s*→\s*/g, " chuyển sang ");
  out = out.replace(/\s*&\s*/g, " và ");
  out = out.replace(/\s*\+\s*/g, " cộng ");

  // Xóa các ký tự thừa không đọc được
  out = out.replace(/[#\*_~`]/g, "");
  out = out.replace(/\s+/g, " ").trim();

  return out;
}
