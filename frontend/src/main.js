import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Font Awesome
import { library } from '@fortawesome/fontawesome-svg-core'
import { faChartBar, faList, faPlus, faBell, faSignOutAlt, faEnvelope, faHourglass, faCheck, faTimes, faSearch, faFile, faSave, faPaperPlane, faSync, faEye, faEyeSlash, faPencil } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import '@fortawesome/fontawesome-free/css/all.min.css'

library.add(faChartBar, faList, faPlus, faBell, faSignOutAlt, faEnvelope, faHourglass, faCheck, faTimes, faSearch, faFile, faSave, faPaperPlane, faSync, faEye, faEyeSlash, faPencil)

const app = createApp(App)
app.component('font-awesome-icon', FontAwesomeIcon)
app.use(createPinia())
app.use(router)
app.mount('#app')
