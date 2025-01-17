#!/usr/bin/env node
import {getOrganicResults} from './commands/organicResults.js'
import {getGoogleScreenshot} from './commands/googleScreenshot.js'
import {getPagePDF} from './commands/pagePDF.js'

import whatsweb from 'whatsapp-web.js';
import qrcode from 'qrcode-terminal';
import chalk from 'chalk';
import {unlinkSync} from 'fs';

const {Client, LocalAuth, MessageMedia} = whatsweb
const client = new Client({ authStrategy: new LocalAuth() });

client.on('qr', qr => {
    console.log('🎆🎉🎊✨');
    qrcode.generate(qr, {small: true});
});

client.on('ready', () => {
    console.clear();
    console.log(chalk.blueBright('esperando mensajes... ☁️☁️'));
});

/**
 * ? región de notas y cosas por hacer
 * obj: modularizar cada comando en un archivo diferente
 * o al menos reducir el tamaño del bloque de los comandos realizando las operaciones en internet fuera de este archivo
*/


client.on('message', async msg => {
    const message = msg.body
    const chat = msg.getChat();
    const msgArray = message.split(' '); 
    const command = msgArray[0]

    if (command === '.google') {
        //! si el mensaje tiene un error de sintaxis, devolver mensaje de error
        if (msgArray.length !== 2 && isNaN(msgArray[2])) {
            msg.reply('poorly written command, please check if page index is a number');
            return ;
        }

        // la segunda parte del comando sería la que dice qué se va a buscar en google
        // esta debe ser dada con _ en vez de "espacios"
        let toSearch = msgArray[1].replace('_', ' ');
        // gets google first pages of a search
        let googleResults = await getOrganicResults(toSearch);
        
        if (msgArray.length === 2) { //? no page index given
            // get screenshot of google search 
            await getGoogleScreenshot(toSearch);

            let captionToSend = '';
            // find screenshot file
            let mediaTosend = await MessageMedia.fromFilePath('./dowloads/googleResult.png');
            
            googleResults.forEach((loadedPage, i) => captionToSend += `🌸 ↣ ${i+1}: ${loadedPage.title}\n`);
            chat.sendMessage(mediaTosend, {caption: captionToSend});

            //delete screenshot file (to clean folder)
            unlinkSync('./dowloads/googleResult.png');
        } else { //? page index given, return page 
            let pageIndex = parseInt(msgArray[2]) -1
            let pageLink = googleResults[pageIndex]["link"];

            await getPagePDF(pageLink)
            let mediaTosend = await MessageMedia.fromFilePath('./dowloads/page.pdf');
            chat.sendMessage(`la página es: ${pageLink} 🍄`);
            chat.sendMessage(mediaTosend);
            
            // limpiar la carpeta de descargas
            unlinkSync('./dowloads/page.pdf')
        }
    } else if (command === '.link') {
        
    }
})



client.initialize();
