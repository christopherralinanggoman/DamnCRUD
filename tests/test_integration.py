import sys
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture
def driver():
    options = Options()
    # options.headless = True  # Uncomment jika ingin menjalankan headless

    if sys.platform.startswith("linux"):
        # Pada Linux, geckodriver biasanya sudah terpasang di /usr/bin/geckodriver
        service = Service("/usr/bin/geckodriver")
    elif sys.platform.startswith("win"):
        # Gunakan path Windows saat dijalankan secara lokal
        service = Service(r"C:\Program Files\GeckoDriver\geckodriver.exe")
    else:
        raise Exception("Platform tidak didukung!")

    driver = webdriver.Firefox(service=service, options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

@pytest.mark.order(1)
def test_login_success(driver):
    driver.get("http://127.0.0.1:8000/login.php")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "inputUsername")))
    driver.find_element(By.ID, "inputUsername").send_keys("admin")
    driver.find_element(By.ID, "inputPassword").send_keys("nimda666!")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    # Tunggu hingga elemen "Sign out" muncul sebagai indikasi login berhasil
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Sign out")))
    assert "Sign out" in driver.page_source

@pytest.mark.order(2)
def test_add_contact(driver):
    # Login first
    driver.get("http://127.0.0.1:8000/login.php")
    driver.find_element(By.ID, "inputUsername").send_keys("admin")
    driver.find_element(By.ID, "inputPassword").send_keys("nimda666!")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Wait until index page loads and the "Add New Contact" link is present
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Add New Contact")))
    
    # Click "Add New Contact" to go to create.php
    driver.find_element(By.LINK_TEXT, "Add New Contact").click()

    # Now on create.php, wait until the form is loaded by checking the presence of the "name" field
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name")))

    # Fill in the form on create.php
    driver.find_element(By.ID, "name").send_keys("Selenium Test")
    driver.find_element(By.ID, "email").send_keys("selenium@test.com")
    driver.find_element(By.ID, "phone").send_keys("1234567890")
    driver.find_element(By.ID, "title").send_keys("QA Engineer")

    # Click the Save button
    driver.find_element(By.XPATH, "//input[@type='submit' and @value='Save']").click()

    # Wait for the form to be processed and for a redirection to index.php,
    # and wait until the new contact ("Selenium Test") appears in the page body.
    WebDriverWait(driver, 10).until(EC.url_contains("index.php"))
    WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Selenium Test"))

    # Verify that the new contact is present on index.php
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Selenium Test" in body_text


@pytest.mark.order(3)
def test_update_contact(driver):
    # Login terlebih dahulu
    driver.get("http://127.0.0.1:8000/login.php")
    driver.find_element(By.ID, "inputUsername").send_keys("admin")
    driver.find_element(By.ID, "inputPassword").send_keys("nimda666!")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(2)
    
    # Akses halaman index, lalu klik tombol "edit" untuk kontak yang ingin diubah
    driver.get("http://127.0.0.1:8000/index.php")
    edit_button = driver.find_element(By.LINK_TEXT, "edit")
    edit_button.click()
    
    # Pada halaman update.php, ubah data kontak (misal, ubah nama kontak)
    name_field = driver.find_element(By.ID, "name")
    name_field.clear()
    name_field.send_keys("Selenium Test Updated")
    
    # Klik tombol Update
    update_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Update']")
    update_button.click()
    
    # Verifikasi bahwa data sudah diperbarui di halaman index
    time.sleep(2)
    driver.get("http://127.0.0.1:8000/index.php")
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Selenium Test Updated" in body_text

@pytest.mark.order(4)
def test_delete_contact(driver):
    # Login terlebih dahulu
    driver.get("http://127.0.0.1:8000/login.php")
    driver.find_element(By.ID, "inputUsername").send_keys("admin")
    driver.find_element(By.ID, "inputPassword").send_keys("nimda666!")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(2)
    
    # Akses halaman index, lalu klik tombol "delete" untuk menghapus kontak
    driver.get("http://127.0.0.1:8000/index.php")
    delete_button = driver.find_element(By.LINK_TEXT, "delete")
    delete_button.click()
    
    # Tangani dialog konfirmasi JavaScript
    alert = driver.switch_to.alert
    alert.accept()
    
    # Verifikasi bahwa kontak tidak lagi muncul di daftar
    time.sleep(2)
    driver.get("http://127.0.0.1:8000/index.php")
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Selenium Test Updated" not in body_text

@pytest.mark.order(5)
def test_logout(driver):
    # Login terlebih dahulu
    driver.get("http://127.0.0.1:8000/login.php")
    driver.find_element(By.ID, "inputUsername").send_keys("admin")
    driver.find_element(By.ID, "inputPassword").send_keys("nimda666!")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(2)
    
    # Akses halaman index, lalu klik tombol "Sign out"
    driver.get("http://127.0.0.1:8000/index.php")
    signout_button = driver.find_element(By.LINK_TEXT, "Sign out")
    signout_button.click()
    time.sleep(2)
    
    # Verifikasi bahwa user diarahkan kembali ke halaman login
    assert "login.php" in driver.current_url
