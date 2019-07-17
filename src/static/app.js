
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

    const [statementMonth, setStatementMonth] = useState(months[date.getMonth()])
    const [statementYear, setStatementYear] = useState(date.getFullYear() + "")
    const fileInputRef = useRef(null)
    const [statementFileName, setStatementFileName] = useState("No file selected")

    return (
        <>
            <label htmlFor="year-select">Year</label>
            <select id="year-select"
                value={statementYear}
                onChange={e => setStatementYear(e.target.value)}
            >
                {years.map(year => (
                    <option value={year} key={year}>{year}</option>
                ))}
            </select>

            <label htmlFor="month-select">Month</label>
            <select id="month-select"
                value={statementMonth}
                onChange={e => setStatementMonth(e.target.value)}
            >
                    {months.map(month => (
                        <option value={month} key={month}>{month}</option>
                    ))}
            </select>
            <input
                type="file"
                label="Choose statement file"
                ref={fileInputRef}
                onChange={() => {
                    setStatementFileName(fileInputRef.current.files[0].name)
                }}
            />

            <div>
                {statementMonth}
            </div>
            <div>
                {statementYear}
            </div>
            <div>
                {statementFileName}
            </div>
        </>
    )

}

ReactDOM.render(<App/>, document.querySelector('#react-root'));
