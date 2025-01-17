import puppeteer from 'puppeteer';

/**
 * @param {String} search - searchs it on google and downloads a png screenshot
 */
export async function getGoogleScreenshot(search) {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.setDefaultNavigationTimeout(0); 
    await page.setViewport({
        width: 412,
        height: 732,
        isMobile: true,
        deviceScaleFactor: 2
    });
    await page.goto('https://www.google.com/search?q=' + encodeURIComponent(search));
    await page.screenshot({path: '/home/zodak/home/dev/whatsbotv2/dowloads/googleResult.png'});
    await browser.close();
}