import './style.css'
import { listProviders } from './providers.ts'
// `provider.ts` is imported and the listProviders function is called at bottom of file

// this querySelector is used to select the element with the id of `app` and set its innerHTML to the following:
document.querySelector<HTMLDivElement>('#app')!.innerHTML = `
  <div>
    <h1>Validator Swarm Local Signing Interface</h1>
    <div id="providerButtons"></div>
  </div>
`

// The listProviders function is called passing an argument so that we can execute code that
//  will be responsible for connecting to the provider using `eth_requestAccounts`
// and then using appendChild to add each button to the element within the div with the id of `providerButtons`
listProviders(document.querySelector<HTMLDivElement>('#providerButtons')!)

