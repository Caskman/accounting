import React, { useEffect, useState, useRef } from 'react'
import './App.css'

const download = (filename, text) => {
  const element = document.createElement('a')
  element.setAttribute(
    'href',
    'data:text/plain;charset=utf-8,' + encodeURIComponent(text)
  )
  element.setAttribute('download', filename)

  element.style.display = 'none'
  document.body.appendChild(element)

  element.click()

  document.body.removeChild(element)
}

const getAccessString = () => {
  return localStorage.getItem('access_string')
}

const putAccessString = access_string => {
  localStorage.setItem('access_string', access_string)
}

const getApigw = () => getAccessString().split('.')[0]

const getUrl = route => {
  const apigw = getApigw()
  return `https://${apigw}.execute-api.us-east-1.amazonaws.com/Prod/base?route=${route}`
}

const getAuthToken = () => getAccessString().split('.')[1]

const fetchApi = async (route, extraBody) => {
  const url = getUrl(route)
  let body = {
    auth: getAuthToken(),
  }
  if (extraBody) {
    body = {
      ...body,
      ...extraBody,
    }
  }
  const options = {
    method: 'post',
    body: JSON.stringify(body),
  }
  const response = await fetch(url, options).then(r => r.json())
  return response.data
}

function App() {
  const rulesUploadRef = useRef(null)
  const [loadingText, setLoadingText] = useState('')
  const [toastText, setToastText] = useState('')
  const [toastTimeout, setToastTimeout] = useState(null)
  const [accessStringInput, setAccessStringInput] = useState('')
  const [validAccessString, setValidAccessString] = useState(true)

  const toast = text => {
    if (toastTimeout) {
      clearTimeout(toastTimeout)
    }
    setToastText(text)
    const timeoutId = setTimeout(() => {
      clearTimeout(toastTimeout)
      setToastTimeout(null)
      setToastText('')
    }, 10000)
    setToastTimeout(timeoutId)
  }

  const errorHandler = async fn => {
    try {
      await fn()
    } catch (e) {
      toast('Error occurred')
      setLoadingText('')
      throw e
    }
  }

  const uploadRules = async () => {
    errorHandler(async () => {
      const file = rulesUploadRef.current.files[0]

      const contents = await new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.readAsText(file, 'UTF-8')
        reader.onload = e => resolve(e.target.result)
        reader.onerror = e => reject(e)
      })

      setLoadingText('Uploading Rules')
      await fetchApi('rules_put', { rules: contents })
      setLoadingText('')
      toast('Uploading Rules Successful!')
    })
  }

  const downloadTransactions = async () => {
    errorHandler(async () => {
      setLoadingText('Downloading Transactions')
      const transactions = await fetchApi('transactions_get')
      setLoadingText('')
      download('transactions.csv', transactions)
    })
  }

  const downloadRules = async () => {
    errorHandler(async () => {
      setLoadingText('Downloading Rules')
      const transactions = await fetchApi('rules_get')
      setLoadingText('')
      download('classification_rules.csv', transactions)
    })
  }

  const classify = async () => {
    errorHandler(async () => {
      setLoadingText('Classifying')
      await fetchApi('classify')
      setLoadingText('')
      toast('Classification Successful!')
    })
  }

  const verifyAccessString = () => {
    if (accessStringInput) {
      putAccessString(accessStringInput)
      setValidAccessString(true)
    }
  }

  useEffect(() => {
    const localStorageAccessString = getAccessString()
    if (!localStorageAccessString) {
      setValidAccessString(false)
    }
  }, [])

  const showModal = !!loadingText || !validAccessString

  return (
    <div className="finance-viewer">
      {showModal ? (
        <div className="modal">
          <div className="modal-body">
            {loadingText ? (
              <div className="loader-container">
                <div>{loadingText}</div>
                <div class="lds-hourglass"></div>
              </div>
            ) : null}
            {!validAccessString ? (
              <section>
                <section>Please provide access string</section>
                <section>
                  <input
                    type="text"
                    onChange={e => setAccessStringInput(e.target.value)}
                  />
                  <button onClick={() => verifyAccessString()}>Go</button>
                </section>
              </section>
            ) : null}
          </div>
        </div>
      ) : null}
      {toastText ? <div className="toast">{toastText}</div> : null}
      <header>
        <button onClick={() => setValidAccessString(false)}>
          Set Access String
        </button>
      </header>
      <section className="main-body">
        <nav className="side-nav"></nav>
        <section className="main">
          <section>
            <p>
              Click to download all transactions as a csv which includes their
              classifications
            </p>
            <button onClick={() => downloadTransactions()}>
              Download Transactions
            </button>
          </section>
          <section>
            <p>Click to download all classification rules as a csv</p>
            <button onClick={() => downloadRules()}>Download Rules</button>
          </section>
          <section>
            <p>You can upload an updated rules file</p>
            <input type="file" ref={rulesUploadRef} />
            <button onClick={() => uploadRules()}>Upload Rules</button>
          </section>
          <section>
            <p>
              After updating the rules file, click this to classify all
              transactions again. You can then download transactions above to
              get all transactions with their updated classifications
            </p>
            <button onClick={() => classify()}>Classify Transactions</button>
          </section>
        </section>
      </section>
      <footer></footer>
    </div>
  )
}

export default App
