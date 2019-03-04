import base64
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


def wsm_login(url, username, password, port):

    binary_path = r"C:\Users\JMILLER.AD\AppData\Local\Mozilla Firefox\firefox.exe"

    # Building the profile, setting the port equal to tor on localhost
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.socks", "127.0.0.1")
    profile.set_preference("network.proxy.socks_port", port)
    profile.set_preference("network.proxy.socks_remote_dns", True)

    # Tor Browser settings, to bypass fingerprinting
    profile.set_preference("places.history.enabled", False)
    profile.set_preference("privacy.clearOnShutdown.offlineApps", True)
    profile.set_preference("privacy.clearOnShutdown.passwords", True)
    profile.set_preference("privacy.clearOnShutdown.siteSettings", True)
    profile.set_preference("privacy.sanitize.sanitizeOnShutdown", True)
    profile.set_preference("signon.rememberSignons", False)
    profile.set_preference("network.dns.disablePrefetch", True)
    profile.set_preference("network.http.sendRefererHeader", 0)

    profile.update_preferences()

    # Setting the binary path for firefox
    binary = FirefoxBinary(binary_path)

    # make browser headless and launch
    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(firefox_binary=binary, firefox_profile=profile, options=options)
    driver.get(url)

    # Complete first captcha to get to login page
    while True:
        im = get_captcha_image(driver)
        im.show()
        captcha_text = input("Please enter captcha text")
        driver.find_element_by_xpath("//input[@id='form_captcha']").send_keys(captcha_text)
        # Submit the form
        driver.find_element_by_xpath("//button[@class=' btn btn-block btn3d btn-info']").click()
    
        # break out of loop if captcha succeeded
        if captcha_succeeded(driver):
            break
    
    # Complete the actual login page
    while True:
        # Enter the username
        input_element = driver.find_element_by_xpath("//input[@id='form_username']")
        input_element.clear()  # Clear field because if captcha failed the username will still remain
        input_element.send_keys(username)
        # Enter the password
        input_element = driver.find_element_by_xpath("//input[@id='form_password']")
        input_element.send_keys(password)

        im = get_captcha_image(driver)
        im.show()

        captcha_text = input("Please enter captcha text")
        driver.find_element_by_xpath("//input[@id='form_captcha']").send_keys(captcha_text)

        # Submit the form
        driver.find_element_by_xpath("//button[@class='btn btn-sm btn-primary']").click()
        
        # break out of loop if captcha succeeded
        if captcha_succeeded(driver):
            break

    return driver.get_cookies()

def get_captcha_image(driver):
    # find the captcha element
    ele_captcha = driver.find_element_by_xpath("//img[@class='captcha_image']")
    # get the captcha as a base64 string
    img_captcha_base64 = driver.execute_async_script("""
        var ele = arguments[0], callback = arguments[1];
        ele.addEventListener('load', function fn(){
          ele.removeEventListener('load', fn, false);
          var cnv = document.createElement('canvas');
          cnv.width = this.width; cnv.height = this.height;
          cnv.getContext('2d').drawImage(this, 0, 0);
          callback(cnv.toDataURL('image/jpeg').substring(22));
        }, false);
        ele.dispatchEvent(new Event('load'));
        """, ele_captcha)

    # Open image and have user input answer
    return Image.open(BytesIO(base64.b64decode(img_captcha_base64)))
    
def captcha_succeeded(driver):
    try:
        # still on login page, try again
        driver.find_element_by_xpath(
            "//div[@class, 'alert alert-danger width-100' and contains(text(),'One or more errors occured')]")
        return False
    except:
        # captcha did not fail.
        return True

if __name__ == "__main__":
    get_captcha_image()