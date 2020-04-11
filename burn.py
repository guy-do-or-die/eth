import re
import sys
import ipdb
import time
import uuid
import signal
import random
import logging
import subprocess

from datetime import datetime, timedelta
from itertools import cycle

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities, ActionChains

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By

from selenium.common.exceptions import NoAlertPresentException

from utils import log as base_log, wait

from mongoengine.queryset.visitor import Q
from db import Guy

import config

from mouse import x_i, y_i


errors_count = 0
cmd = 'surf'
proc = 0
n = 0


def log(*args, **kwargs):
    global errors_count, cmd, n, proc
    kwargs['proc'] = proc

    base_log(*args, **kwargs)

    if kwargs.get('type') == 'error':
        if errors_count == 0:
            pers('{}_{}'.format(proc, cmd), n)

        errors_count += 1

        log('errors count: {}'.format(errors_count))


def setup_driver(proxy=False, detached=False, driver=None, headless=True):
    try:
        chrome_options = Options()
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-logging')

        headless and chrome_options.add_argument('--headless')

        prefs = {'profile.managed_default_content_settings.images': 2}
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_experimental_option('detach', False)

        dc = DesiredCapabilities.CHROME
        dc['loggingPrefs'] = {'browser': 'ALL'}

        if proxy:
            proxy = Proxy()
            proxy.proxy_type = ProxyType.MANUAL
            proxy.socks_proxy = config.PROXY
            proxy.http_proxy = config.PROXY
            proxy.ssl_proxy = config.PROXY
            proxy.add_to_capabilities(dc)

        driver = webdriver.Chrome(chrome_options=chrome_options,
                                  desired_capabilities=dc)

        max_wait = config.PROXY_LOAD_TIMEOUT if proxy else config.LOAD_TIMEOUT
        driver.set_window_size(1000, 1000)
        driver.set_page_load_timeout(max_wait)
        driver.set_script_timeout(max_wait)

        setattr(driver, 'proxy', proxy)
    except Exception as e:
        log(e, type='error')

    if not detached:
        def handler(*args, **kwargs):
            try:
                if driver:
                    driver.stop_client()
                    driver.close()
                    driver.quit()
            except:
                log('quitting')

            signal.signal(signal.SIGINT, signal.SIG_IGN)

        signal.signal(signal.SIGINT, handler)

    return driver


def make_a_guy():
    guy = Guy()
    guy.email = f'guy.do.or.die+{uuid.uuid4()}@gmail.com'
    return guy


def claim(driver, guy):
    claim = wait(driver, EC.presence_of_element_located((By.ID, 'get-free')))

    action =  ActionChains(driver);
    action.move_to_element(claim);
    action.perform();

    for mouse_x, mouse_y in list(zip(x_i, y_i))[:5]:
        action.move_by_offset(mouse_x, mouse_y);
        action.perform();

    claim.click()
    time.sleep(1)

    guy.claimed = datetime.now()
    guy.save()


def reg():

    while True:
        guy = make_a_guy()

        try:
            driver = setup_driver()
            driver.get(config.REF_URL)

            signup_btn = wait(driver, EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'a[href="/signup"]')))

            signup_btn.click()

            signup_container = wait(driver, EC.presence_of_element_located(
                (By.CLASS_NAME, 'signup-container')))


            driver.find_element_by_class_name('email-input').send_keys(guy.email)
            driver.find_element_by_class_name('pass-input1').send_keys(config.PASSWORD)
            driver.find_element_by_class_name('pass-input2').send_keys(config.PASSWORD)
            driver.find_element_by_id('btnform').click()
            guy.save()

            claim(driver, guy)

        except Exception as e:
            log(str(e))
            if errors_count > 5:
                signal.signal(signal.SIGINT, signal.SIG_IGN)
        finally:
            log(f'registered {guy.email}')
            driver.close()


def check():

    driver = setup_driver(headless=1)

    while True:
        dt = datetime.now() - timedelta(minutes=5)

        N = 5
        q = Q(claimed__lt=dt) | Q(claimed=None)

        count = Guy.objects(q).count()
        offset = random.randint(N, count) - N

        guys = Guy.objects(q).skip(offset).limit(N)

        log(f'check {N} guys from {offset} one, out of {count} available')

        for guy in guys:
            try:
                driver.get(config.LOGIN_URL)

                signup_container = wait(driver, EC.presence_of_element_located(
                    (By.CLASS_NAME, 'signup-container')))

                driver.find_element_by_class_name('email-input').send_keys(guy.email)
                driver.find_element_by_class_name('pass-input').send_keys(config.PASSWORD)
                driver.find_element_by_id('btnform').click()

                try:
                    balance = wait(driver, EC.presence_of_element_located((By.ID, 'balance')))
                    guy.balance = float(balance.text.split()[0])
                except:
                    log(f'problem logging in as {guy.email}')
                    guy.problems += 1
                    guy.save()
                    continue

                try:
                    reward = driver.find_element_by_class_name('result').text
                    claim(driver, guy)
                    guy.save()

                    log(f'successfully claimed {reward} for {guy.email} ({guy.balance:.8f})')
                except Exception as e:
                    log(f'already claimed for {guy.email}')

            except Exception as e:
                log(str(e))
                if errors_count > 5:
                    signal.signal(signal.SIGINT, signal.SIG_IGN)
            finally:
                #driver.close()
                driver.get(config.LOGOUT_URL)
                signup_btn = wait(driver, EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'a[href="/signup"]')))
