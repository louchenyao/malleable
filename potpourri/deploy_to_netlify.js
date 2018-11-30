const fs = require('fs');
const NetlifyAPI = require('netlify')

async function read_token() {
    return new Promise(function(resolve, reject) {
        fs.readFile("./netlify_token.txt", (err, data) => {
            if (err) reject(err)
            else resolve(data.toString())
        })
    })
}

async function deploy() {
    let token = await read_token()
    const client = new NetlifyAPI(token)
    return client.deploy("984a348d-133e-479d-967d-d885f99c0a7c", "../public")
}

async function main() {
    let r = await deploy()
    console.log(r)
}

main()