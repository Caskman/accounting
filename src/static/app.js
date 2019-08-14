
const { useState, useRef } = React;

const App = function({}) {

    const date = new Date()

    const months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    const years = []
    for (let i = date.getFullYear() - 3; i < date.getFullYear() + 2; i++) {
        years.push("" + i)
    }
    // const accountTypes = [
    //     "boacredit",
    //     "boadebit",
    //     "llbeanmccredit",
    // ]

    const labels = [
        "boaprimary8571",
        "boasecondary9174",
        "boa2236",
        "llbeanmastercard7771",
    ]

    const labelsToAccountTypes = {
        "boaprimary8571": "boadebit",
        "boasecondary9174": "boadebit",
        "boa2236": "boacredit",
        "llbeanmastercard7771": "llbeanmccredit",
    }

    const fileInputRef = useRef(null)

    const [statementMonth, setStatementMonth] = useState(months[date.getMonth()])
    const [statementYear, setStatementYear] = useState(date.getFullYear() + "")
    const [statementAccountType, setStatementAccountType] = useState("")
    const [statementFileName, setStatementFileName] = useState("No file selected")
    const [statementLabel, setStatementLabel] = useState("")

    return (
        <>
            <div>
                <label htmlFor="year-select">Year</label>
                <select id="year-select"
                    value={statementYear}
                    onChange={e => setStatementYear(e.target.value)}
                >
                    {years.map(year => (
                        <option
                            value={year}
                            key={year}
                        >
                            {year}
                        </option>
                    ))}
                </select>
            </div>

            <div>
                <label htmlFor="month-select">Month</label>
                <select id="month-select"
                    value={statementMonth}
                    onChange={e => setStatementMonth(e.target.value)}
                >
                    {months.map(month => (
                        <option
                            value={month}
                            key={month}
                        >
                            {month}
                        </option>
                    ))}
                </select>
            </div>

            {/* <div>
                <label htmlFor="type-select">Type</label>
                <select
                    id="type-select"
                    value={statementAccountType}
                    onChange={e => setStatementAccountType(e.target.value)}
                >
                    <option key="nothing">Choose Account Type</option>
                    {accountTypes.map(type => (
                        <option
                            value={type}
                            key={type}
                        >
                            {type}
                        </option>
                    ))}
                </select>
            </div> */}

            <div>
                <label htmlFor="label-select">Label</label>
                <select
                    id="label-select"
                    value={statementLabel}
                    onChange={e => {
                        setStatementLabel(e.target.value)
                        setStatementAccountType(labelsToAccountTypes[e.target.value])
                    }}
                >
                    <option key="nothing">Choose Label</option>
                    {labels.map(label => (
                        <option
                            value={label}
                            key={label}
                        >
                            {label}
                        </option>
                    ))}
                </select>
            </div>

            <div>
                <input
                    type="file"
                    label="Choose statement file"
                    ref={fileInputRef}
                    onChange={() => {
                        setStatementFileName(fileInputRef.current.files[0].name)
                    }}
                />
            </div>

            <div>
                {statementMonth}
            </div>
            <div>
                {statementYear}
            </div>
            <div>
                {statementFileName}
            </div>
            <div>
                {statementAccountType}
            </div>
            <div>
                {statementLabel}
            </div>
            <div>
                <button onClick={() => 
                    business.upload(
                        statementYear,
                        statementMonth,
                        statementAccountType,
                        statementLabel,
                        fileInputRef.current.files[0],
                    ).then(response => {
                        console.log(response)
                    })
                }>
                    Upload
                </button>
            </div>
        </>
    )

}

ReactDOM.render(<App/>, document.querySelector('#react-root'));
