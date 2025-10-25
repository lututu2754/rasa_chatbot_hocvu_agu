from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "chatbot_hocvu_agu",
    "charset": "utf8mb4",
}


# Code để kết nối với CSDL
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
except mysql.connector.Error as err:
    print(f"Lỗi kết nối MySQL: {err}")
    conn = None
    cursor = None


class ActionThongTinPhongBan(Action):
    def name(self) -> Text:
        return "action_thong_tin_phong_ban"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        phong = tracker.get_slot("ten_phong")  # Lấy tên phòng từ slot
        if not phong:
            dispatcher.utter_message(
                text="Bạn vui lòng cung cấp tên phòng bạn muốn tìm."
            )
            return []

        query = "SELECT * FROM phong_ban WHERE ten_phong LIKE %s"
        cursor.execute(query, (f"%{phong}%",))
        result = cursor.fetchone()

        if result:
            msg = (
                f"Thông tin {result['ten_phong']}:\n"
                f"SĐT: {result['so_dien_thoai']}\n"
                f"Email: {result['email']}\n"
                f"Giờ làm việc: {result['gio_lam_viec']}\n"
                f"Địa chỉ: {result['dia_chi']}"
            )
            dispatcher.utter_message(text=msg)
        else:
            dispatcher.utter_message(text=f"Không tìm thấy phòng ban '{phong}'.")

        return []


class ActionThuTucHocVu(Action):
    def name(self) -> Text:
        return "action_thu_tuc_hocvu"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        ten_thutuc = tracker.get_slot("ten_thutuc")
        if not ten_thutuc:
            dispatcher.utter_message(text="Bạn vui lòng cung cấp tên thủ tục học vụ.")
            return []

        query = "SELECT * FROM hocvu_thutuc WHERE ten_thutuc LIKE %s"
        cursor.execute(query, (f"%{ten_thutuc}%",))
        result = cursor.fetchone()

        if result:
            msg = (
                f"Thủ tục: {result['ten_thutuc']}\n"
                f"Mô tả: {result['mo_ta']}\n"
                f"Yêu cầu: {result['yeu_cau']}"
            )
            dispatcher.utter_message(text=msg)
        else:
            dispatcher.utter_message(text=f"Không tìm thấy thủ tục '{ten_thutuc}'.")

        return []


class ActionThongBao(Action):
    def name(self) -> Text:
        return "action_thong_bao"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        phong = tracker.get_slot("ten_phong")
        if not phong:
            dispatcher.utter_message(
                text="Bạn vui lòng cung cấp tên phòng ban để xem thông báo."
            )
            return []

        query = """
        SELECT tb.tieu_de, tb.noi_dung, tb.ngay_dang 
        FROM thong_bao tb 
        JOIN phong_ban pb ON tb.phong_id = pb.ma_phong 
        WHERE pb.ten_phong LIKE %s 
        ORDER BY tb.ngay_dang DESC
        """
        cursor.execute(query, (f"%{phong}%",))
        results = cursor.fetchall()

        if results:
            msg = "Các thông báo mới:\n"
            for r in results:
                msg += f"- {r['tieu_de']} ({r['ngay_dang']}): {r['noi_dung']}\n"
            dispatcher.utter_message(text=msg)
        else:
            dispatcher.utter_message(
                text=f"Không có thông báo nào cho phòng '{phong}'."
            )

        return []


class ActionHuongDan(Action):
    def name(self) -> Text:
        return "action_huong_dan_he_thong"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        he_thong = tracker.get_slot("ten_he_thong")
        if not he_thong:
            dispatcher.utter_message(
                text="Bạn vui lòng cung cấp tên hệ thống để xem hướng dẫn."
            )
            return []

        query = "SELECT * FROM huong_dan WHERE ten_he_thong LIKE %s"
        cursor.execute(query, (f"%{he_thong}%",))
        result = cursor.fetchone()

        if result:
            msg = (
                f"Hướng dẫn sử dụng {result['ten_he_thong']}:\n"
                f"{result['noi_dung']}\n"
                f"Truy cập tại: {result['link_truy_cap']}"
            )
            dispatcher.utter_message(text=msg)
        else:
            dispatcher.utter_message(
                text=f"Không tìm thấy hướng dẫn cho hệ thống '{he_thong}'."
            )

        return []
