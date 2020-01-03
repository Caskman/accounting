(this["webpackJsonpfinance-viewer"]=this["webpackJsonpfinance-viewer"]||[]).push([[0],{11:function(e,t,n){},13:function(e,t,n){},14:function(e,t,n){"use strict";n.r(t);var a=n(0),c=n.n(a),r=n(4),s=n.n(r),o=(n(11),n(2)),l=n(1),i=n.n(l),u=n(5),f=(n(13),function(e,t){var n=document.createElement("a");n.setAttribute("href","data:text/plain;charset=utf-8,"+encodeURIComponent(t)),n.setAttribute("download",e),n.style.display="none",document.body.appendChild(n),n.click(),document.body.removeChild(n)}),d=function(){return localStorage.getItem("access_string")},m=function(e){var t=d();return"https://".concat(t,".execute-api.us-east-1.amazonaws.com/Prod/base?route=").concat(e)},p=function(e,t){var n,a;return i.a.async((function(c){for(;;)switch(c.prev=c.next){case 0:return n=m(e),c.next=3,i.a.awrap(fetch(n,Object(u.a)({method:"post"},t)).then((function(e){return e.json()})));case 3:return a=c.sent,c.abrupt("return",a.data);case 5:case"end":return c.stop()}}))};var v=function(){var e=Object(a.useRef)(null),t=Object(a.useState)(""),n=Object(o.a)(t,2),r=n[0],s=n[1],l=Object(a.useState)(""),u=Object(o.a)(l,2),m=u[0],v=u[1],w=Object(a.useState)(null),h=Object(o.a)(w,2),E=h[0],b=h[1],y=Object(a.useState)(""),g=Object(o.a)(y,2),x=g[0],k=g[1],C=Object(a.useState)(!0),j=Object(o.a)(C,2),O=j[0],S=j[1],N=function(e){E&&clearTimeout(E),v(e);var t=setTimeout((function(){clearTimeout(E),b(null),v("")}),1e4);b(t)},R=function(e){return i.a.async((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,i.a.awrap(e());case 3:t.next=10;break;case 5:throw t.prev=5,t.t0=t.catch(0),N("Error occurred"),s(""),t.t0;case 10:case"end":return t.stop()}}),null,null,[[0,5]])},T=function(){var e;x&&(e=x,localStorage.setItem("access_string",e),S(!0))};Object(a.useEffect)((function(){d()||S(!1)}),[]);var _=!!r||!O;return c.a.createElement("div",{className:"finance-viewer"},_?c.a.createElement("div",{className:"modal"},c.a.createElement("div",{className:"modal-body"},r,O?null:c.a.createElement("section",null,c.a.createElement("section",null,"Please provide access string"),c.a.createElement("section",null,c.a.createElement("input",{type:"text",onChange:function(e){return k(e.target.value)}}),c.a.createElement("button",{onClick:function(){return T()}},"Go"))))):null,m?c.a.createElement("div",{className:"toast"},m):null,c.a.createElement("header",null,c.a.createElement("button",{onClick:function(){return S(!1)}},"Set Access String")),c.a.createElement("section",{className:"main-body"},c.a.createElement("nav",{className:"side-nav"}),c.a.createElement("section",{className:"main"},c.a.createElement("section",null,c.a.createElement("p",null,"Click to download all transactions as a csv which includes their classifications"),c.a.createElement("button",{onClick:function(){return i.a.async((function(e){for(;;)switch(e.prev=e.next){case 0:R((function(){var e;return i.a.async((function(t){for(;;)switch(t.prev=t.next){case 0:return s("Downloading Transactions"),t.next=3,i.a.awrap(p("transactions_get"));case 3:e=t.sent,s(""),f("transactions.csv",e);case 6:case"end":return t.stop()}}))}));case 1:case"end":return e.stop()}}))}},"Download Transactions")),c.a.createElement("section",null,c.a.createElement("p",null,"Click to download all classification rules as a csv"),c.a.createElement("button",{onClick:function(){return i.a.async((function(e){for(;;)switch(e.prev=e.next){case 0:R((function(){var e;return i.a.async((function(t){for(;;)switch(t.prev=t.next){case 0:return s("Downloading Rules"),t.next=3,i.a.awrap(p("rules_get"));case 3:e=t.sent,s(""),f("classification_rules.csv",e);case 6:case"end":return t.stop()}}))}));case 1:case"end":return e.stop()}}))}},"Download Rules")),c.a.createElement("section",null,c.a.createElement("p",null,"You can upload an updated rules file"),c.a.createElement("input",{type:"file",ref:e}),c.a.createElement("button",{onClick:function(){return i.a.async((function(t){for(;;)switch(t.prev=t.next){case 0:R((function(){var t,n;return i.a.async((function(a){for(;;)switch(a.prev=a.next){case 0:return t=e.current.files[0],a.next=3,i.a.awrap(new Promise((function(e,n){var a=new FileReader;a.readAsText(t,"UTF-8"),a.onload=function(t){return e(t.target.result)},a.onerror=function(e){return n(e)}})));case 3:return n=a.sent,s("Uploading Rules"),a.next=7,i.a.awrap(p("rules_put",{body:JSON.stringify({rules:n})}));case 7:s(""),N("Uploading Rules Successful!");case 9:case"end":return a.stop()}}))}));case 1:case"end":return t.stop()}}))}},"Upload Rules")),c.a.createElement("section",null,c.a.createElement("p",null,"After updating the rules file, click this to classify all transactions again. You can then download transactions above to get all transactions with their updated classifications"),c.a.createElement("button",{onClick:function(){return i.a.async((function(e){for(;;)switch(e.prev=e.next){case 0:R((function(){return i.a.async((function(e){for(;;)switch(e.prev=e.next){case 0:return s("Classifying"),e.next=3,i.a.awrap(p("classify"));case 3:s(""),N("Classification Successful!");case 5:case"end":return e.stop()}}))}));case 1:case"end":return e.stop()}}))}},"Classify Transactions")))),c.a.createElement("footer",null))};Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));s.a.render(c.a.createElement(v,null),document.getElementById("root")),"serviceWorker"in navigator&&navigator.serviceWorker.ready.then((function(e){e.unregister()}))},6:function(e,t,n){e.exports=n(14)}},[[6,1,2]]]);
//# sourceMappingURL=main.bfc9cf27.chunk.js.map