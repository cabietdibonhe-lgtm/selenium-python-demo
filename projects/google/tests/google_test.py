from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


# 1. Mở trình duyệt Chrome
driver = webdriver.Chrome()  # Selenium 4 sẽ tự tải ChromeDriver giúp bạn

# 2. Mở trang Google
driver.get("https://www.google.com")

# 3. Tìm ô nhập search (name="q")
search_box = driver.find_element(By.NAME, "q")

# 4. Gõ từ khóa
search_box.send_keys("Hello world")

# 5. Nhấn Enter
search_box.send_keys(Keys.RETURN)

# 6. Chờ 5 giây cho bạn nhìn kết quả
time.sleep(5)

# 7. Đóng trình duyệt
driver.quit()

