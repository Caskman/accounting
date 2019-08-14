
var business = (function() {
    const self = {
        upload: async function(year, month, accountType, label, file) {
            const contents = await new Promise(resolve => {
                const reader = new FileReader();
                reader.onload = () => {
                    resolve(reader.result)
                }
                reader.readAsText(file)
            })

            const data = {
                contents,
                year,
                month,
                accountType,
                label,
            }
            const response = await axios.post("/upload", data)
            return response
        },
    }
    return self
})()
