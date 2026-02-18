module.exports=[49545,a=>{"use strict";var b=a.i(42904),c=a.i(13739),d=a.i(21194);let e=[{id:"branches",label:"Branches"},{id:"builds",label:"Builds"},{id:"backups",label:"Backups"},{id:"upgrade",label:"Upgrade"},{id:"settings",label:"Settings"},{id:"monitor",label:"Monitor"}];function f({projectId:a}){let f=(0,d.usePathname)();return(0,b.jsx)("nav",{className:"border-b border-gray-200 bg-white",children:(0,b.jsx)("div",{className:"flex space-x-8 px-6",children:e.map(d=>{let e=`/app/projects/${a}/${d.id}`,g=f===e||f.startsWith(`${e}/`);return(0,b.jsx)(c.default,{href:e,className:`
                border-b-2 py-4 px-1 text-sm font-medium
                ${g?"border-blue-500 text-blue-600":"border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"}
              `,children:d.label},d.id)})})})}a.s(["ProjectTabs",()=>f])}];

//# sourceMappingURL=6b336_odoo_templates_odooops-console_src_components_odoo-sh_ProjectTabs_tsx_cce1d67d._.js.map