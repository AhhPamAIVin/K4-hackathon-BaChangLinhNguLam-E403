# Reflection — E403 — Ngô Trọng Bảo

## Vai trò và phần tôi làm
- **Vai trò:** Product Developer / Frontend Lead cho dự án Clone VLearn (Nhóm Ba Chàng Lính Ngự Lâm).
- **Các phần trực tiếp đảm nhận & xây dựng:**
  - Thiết kế và phát triển toàn bộ giao diện web học tập VLearn LMS bằng React + Vite.
  - **SlideReaderView & PdfSlidePage:** Xây dựng trình đọc bài giảng (Slide Reader) tương tác cao, hỗ trợ xem slide PDF, điều hướng trang, xem mục lục bài giảng (Outline) và tích hợp khung trò chuyện AI Tutor trực tiếp trên slide.
  - **Hệ thống Navigation SPA:** Tự xây dựng cơ chế chuyển trang Client-side mượt mà (`window.history.pushState` & `popstate`), hỗ trợ điều hướng linh hoạt giữa các trang Trang chủ (`/`), Khóa học của tôi (`/my-courses`), Chi tiết khóa học (`/course-detail`), và Trình đọc Slide (`/reader`).
  - **Giao diện Đa chủ đề (Dark/Light) & Đa ngôn ngữ (VI/EN):** Xây dựng hệ thống CSS Variables quản lý theme linh hoạt và tích hợp bộ từ điển dịch thuật song ngữ (`translations.js`).
  - **Dashboard & Component UI:** Hoàn thiện toàn bộ các component chính như `Navbar`, `WelcomeCard`, `StatsGrid`, `CourseActionCard`, `MyCoursesView` và `CourseDetailView` bám sát giao diện gốc VLearn.

## Một quyết định tôi có thể tự giải thích
- **Quyết định tự viết Vanilla CSS kết hợp CSS Variables thay vì dùng thư viện UI bên thứ ba:**
  - *Lý do:* Giúp kiểm soát hoàn toàn độ chi tiết của giao diện (pixel-perfect, khoảng cách, màu sắc và typography theo đúng chuẩn VLearn). CSS Variables giúp việc toggle chế độ Tối/Sáng (Dark/Light mode) hoạt động tức thì trên toàn bộ trang mà không gây re-render dư thừa.
  - *Điều hướng Custom SPA:* Sử dụng `history.pushState` thay vì cài thêm thư viện router cồng kềnh giúp giảm bớt dung lượng bundle, tối ưu tốc độ load và dễ dàng tinh chỉnh phù hợp với quy mô ứng dụng hackathon.

## AI đã hỗ trợ tôi như thế nào
- **Khởi tạo và dựng khung Component:** AI hỗ trợ sinh nhanh cấu trúc các component React và bố cục CSS linh hoạt, đặc biệt là chia layout responsive split-screen cho giao diện đọc slide.
- **Tạo từ điển đa ngôn ngữ (`translations.js`):** AI giúp chuẩn hóa và sinh tự động tất cả chuỗi văn bản Anh - Việt chuẩn ngữ cảnh ứng dụng LMS giáo dục.
- **Tối ưu hóa xử lý PDF & State Management:** Gợi ý giải pháp quản lý trạng thái render slide PDF và đồng bộ chế độ Dark Mode lên thẻ root (`document.documentElement`).

## Case fail của nhóm và điều tôi học được
- **Case fail:** Khi mới bắt đầu ghép nối tính năng đọc slide và khung chat AI Tutor, nhóm đã cố gắng xử lý quá nhiều logic bất đồng bộ cùng lúc dẫn đến xung đột state khiến trình đọc PDF bị khựng và giật lag khi chuyển trang.
- **Điều học được:** Ưu tiên hàng đầu trong dự án Hackathon là trải nghiệm người dùng mượt mà (Core UX). Nhóm đã quyết định tái cấu trúc lại component `SlideReaderView`, phân tách độc lập giữa việc render PDF và luồng dữ liệu của AI Chat panel, từ đó phục hồi trải nghiệm cuộn và lật slide siêu tốc.

## Nếu làm lại, tôi sẽ thay đổi gì
- **Tách nhỏ Component & Xây dựng Custom Hooks:** Tách các đoạn logic quản lý PDF viewer và Chat history ra các Custom Hooks riêng biệt (`usePdfReader`, `useChatState`) để code trong `SlideReaderView.jsx` sạch sẽ và dễ bảo trì hơn.
- **Bổ sung Automated UI Testing:** Thêm các kịch bản kiểm thử tự động cho việc chuyển đổi ngôn ngữ (VI/EN) và switch theme Dark/Light để đảm bảo tính nhất quán của giao diện khi mở rộng tính năng mới.
