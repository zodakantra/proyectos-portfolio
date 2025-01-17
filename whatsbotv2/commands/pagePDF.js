import puppeteer from 'puppeteer';


/**
 * download the PDF from a specific page 🔗
 * @param {String} pageLink 
 */
export async function getPagePDF(pageLink) {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.setDefaultNavigationTimeout(0); 
    await page.setViewport({
        width: 412,
        height: 732,
        isMobile: true,
        deviceScaleFactor: 2
    });
    await page.goto(link, {waitUntil: 'networkidle2'});
    await page.pdf({path: '/home/zodak/home/dev/whatsbotv2/dowloads/page.pdf', format: 'legal'})
    await browser.close();
}