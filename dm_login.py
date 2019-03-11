import base64
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


def dm_login(url, username, password, port):

    # #binary_path = r"/home/jacob/Desktop/firefox"
    #
    # # Building the profile, setting the port equal to tor on localhost
    # profile = webdriver.FirefoxProfile()
    # profile.set_preference("network.proxy.type", 1)
    # profile.set_preference("network.proxy.socks", "127.0.0.1")
    # profile.set_preference("network.proxy.socks_port", port)
    # profile.set_preference("network.proxy.socks_remote_dns", True)
    #
    # # # Tor Browser settings, to bypass fingerprinting
    # # profile.set_preference("places.history.enabled", False)
    # # profile.set_preference("privacy.clearOnShutdown.offlineApps", True)
    # # profile.set_preference("privacy.clearOnShutdown.passwords", True)
    # # profile.set_preference("privacy.clearOnShutdown.siteSettings", True)
    # # profile.set_preference("privacy.sanitize.sanitizeOnShutdown", True)
    # # profile.set_preference("signon.rememberSignons", False)
    # # profile.set_preference("network.dns.disablePrefetch", True)
    # # profile.set_preference("network.http.sendRefererHeader", 0)
    #
    # profile.update_preferences()
    #
    # # Setting the binary path for firefox
    # #binary = FirefoxBinary(binary_path)
    #
    # # make browser headless
    # options = webdriver.FirefoxOptions()
    # # options.headless = True
    #
    # # driver = webdriver.Firefox(firefox_profile=profile, options=options)
    driver = webdriver.Firefox()

    while True:
        driver.get(url)

        # find the captcha element
        ele_captcha = driver.find_element_by_xpath("//img[@alt='Captcha']")

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
        im = Image.open(BytesIO(base64.b64decode(img_captcha_base64)))
        im.show()
        captcha_text = input("Please enter captcha text")
        driver.find_element_by_xpath("//input[@title='Captcha, case sensitive']").send_keys(captcha_text)

        # Enter the username
        input_element = driver.find_elements_by_xpath(
            "//input[@value='' or @value='{}' and @type='text']".format(
                username))[0]
        input_element.clear()  # Clear field because if captcha failed the username will still remain
        input_element.send_keys(username)
        # Enter the password
        input_element = driver.find_elements_by_xpath("//input[@value='' and @type='password']")[0]
        input_element.send_keys(password)

        # Submit the form
        driver.find_element_by_xpath("//input[@value='Login']").click()

        # try:
        #     driver.find_element_by_xpath(
        #         look for captcha fail message
        #         "//div[contains(@class, 'error') and text()='Captcha was incorrectly entered']")
        #     # captcha failed and error was found; restart loop
        # except:
        #     pass
        try:
            driver.find_element_by_xpath(
                "//div[contains(@class, 'title') and text()='Login with existing user']")
            # still on login page, try again
        except:
            break  # captcha did not fail. Quit loop

    return driver.get_cookies()