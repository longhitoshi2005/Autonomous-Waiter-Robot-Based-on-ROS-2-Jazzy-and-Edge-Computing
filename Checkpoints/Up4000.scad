// =================================================================
// ĐỒ ÁN: AUTONOMOUS ROBOT WAITER SYSTEM
// THIẾT KẾ: KHAY ĐỠ VUÔNG CHO LIDAR C1 (ĐÁY KÍN, KHÔNG VÍT)
// KÍCH THƯỚC CHUẨN: 55.6mm x 55.6mm x 41.3mm
// Hướng dẫn bởi: Giảng viên Robot & AI
// =================================================================

$fn = 60; // Độ mịn bo góc viền ngoài

// --- THAM SỐ CƠ BẢN (Đơn vị: mm) ---
lidar_w    = 55.6;   // Chiều dài đáy LiDAR C1
lidar_l    = 55.6;   // Chiều rộng đáy LiDAR C1

clearance  = 0.5;    // Khoảng hở an toàn để thả LiDAR vào khít (Snug fit)
wall_thick = 2.5;    // Độ dày thành khay bao quanh
base_thick = 2.0;    // Độ dày tấm đáy kín hoàn toàn
tray_depth = 12.0;   // Chiều cao thành nhựa (ôm chắc 1/3 thân dưới của LiDAR)

// Kích thước lòng trong của khay vuông
inner_w = lidar_w + (clearance * 2);
inner_l = lidar_l + (clearance * 2);

// --- THỰC THI TẠO MÔ HÌNH KHAY VUÔNG ---
difference() {
    // 1. Tạo khối hộp đặc bên ngoài (Đã bo viền nhẹ bằng minkowski)
    minkowski() {
        cube([inner_w, inner_l, tray_depth + base_thick - 1]);
        cylinder(r = wall_thick, h = 1);
    }
    
    // 2. Khoét rỗng lòng trong hình vuông, giữ lại đáy kín dày 2mm
    translate([0, 0, base_thick])
        cube([inner_w, inner_l, tray_depth + 2]);
        
    // 3. RÃNH THOÁT DÂY CÁP TÍN HIỆU (CABLE SLOT)
    // Thiết kế một rãnh khuyết rộng 12mm sát đáy để em luồn dây nguồn/cáp dữ liệu ra ngoài
    translate([inner_w / 2 - 6, -wall_thick - 1, base_thick])
        cube([12, wall_thick + 2, tray_depth + 2]);
}