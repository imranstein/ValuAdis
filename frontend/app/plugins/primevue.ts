import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import Toast from 'primevue/toast'
import Calendar from 'primevue/calendar'
import Dropdown from 'primevue/dropdown'
import Card from 'primevue/card'
import Checkbox from 'primevue/checkbox'
import ProgressBar from 'primevue/progressbar'
import Chart from 'primevue/chart'
import Menu from 'primevue/menu'
import Sidebar from 'primevue/sidebar'
import Toolbar from 'primevue/toolbar'
import FileUpload from 'primevue/fileupload'
import Badge from 'primevue/badge'
import Tag from 'primevue/tag'
import Divider from 'primevue/divider'
import Panel from 'primevue/panel'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(PrimeVue, { ripple: true })
  nuxtApp.vueApp.use(ToastService)
  nuxtApp.vueApp.use(ConfirmationService)
  
  // Provide toast service globally
  nuxtApp.provide('toast', useToast())
  
  // Register components globally
  nuxtApp.vueApp.component('Button', Button)
  nuxtApp.vueApp.component('InputText', InputText)
  nuxtApp.vueApp.component('Password', Password)
  nuxtApp.vueApp.component('DataTable', DataTable)
  nuxtApp.vueApp.component('Column', Column)
  nuxtApp.vueApp.component('Dialog', Dialog)
  nuxtApp.vueApp.component('Toast', Toast)
  nuxtApp.vueApp.component('Calendar', Calendar)
  nuxtApp.vueApp.component('Dropdown', Dropdown)
  nuxtApp.vueApp.component('Card', Card)
  nuxtApp.vueApp.component('Checkbox', Checkbox)
  nuxtApp.vueApp.component('ProgressBar', ProgressBar)
  nuxtApp.vueApp.component('Chart', Chart)
  nuxtApp.vueApp.component('Menu', Menu)
  nuxtApp.vueApp.component('Sidebar', Sidebar)
  nuxtApp.vueApp.component('Toolbar', Toolbar)
  nuxtApp.vueApp.component('FileUpload', FileUpload)
  nuxtApp.vueApp.component('Badge', Badge)
  nuxtApp.vueApp.component('Tag', Tag)
  nuxtApp.vueApp.component('Divider', Divider)
  nuxtApp.vueApp.component('Panel', Panel)
  nuxtApp.vueApp.component('TabView', TabView)
  nuxtApp.vueApp.component('TabPanel', TabPanel)
})
