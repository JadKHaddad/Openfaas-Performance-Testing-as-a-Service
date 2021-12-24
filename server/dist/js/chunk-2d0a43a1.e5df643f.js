(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-2d0a43a1"],{"0616":function(t,e,s){"use strict";s.r(e);var n=s("7a23"),o={class:"control-btn-container"};function i(t,e,s,i,r,c){var a=Object(n["A"])("InstallationProcess"),l=Object(n["A"])("Test");return Object(n["v"])(),Object(n["g"])("div",null,[Object(n["h"])("div",o,[Object(n["h"])("button",{type:"button",class:"btn btn-danger btn-block control-btn",id:"kill-btn",onClick:e[0]||(e[0]=function(){return c.killRunningTasks&&c.killRunningTasks.apply(c,arguments)})}," Kill running tasks "),Object(n["h"])("button",{type:"button",class:"btn btn-danger btn-block control-btn",id:"cleanup-btn",onClick:e[1]||(e[1]=function(){return c.deleteAllProjects&&c.deleteAllProjects.apply(c,arguments)})}," Delete all projects ")]),(Object(n["v"])(!0),Object(n["g"])(n["a"],null,Object(n["z"])(r.projects,(function(t){return Object(n["v"])(),Object(n["e"])(a,{key:t,id:t,url:s.url,openfaasUrl:s.openfaasUrl,socket:s.socket,onDelete:function(e){return c.deleteProject(t)}},null,8,["id","url","openfaasUrl","socket","onDelete"])})),128)),(Object(n["v"])(!0),Object(n["g"])(n["a"],null,Object(n["z"])(c.reversedTests,(function(t){return Object(n["v"])(),Object(n["e"])(l,{key:t[0],id:t[0],info:JSON.parse(t[1].info),data:JSON.parse(t[1].data),status:t[1].status,valid:t[1].valid,showPath:!0,url:s.url,openfaasUrl:s.openfaasUrl,pid:t[1].project_name,sid:t[1].script_name,startMinimized:s.minimizeTests,onRestart:c.restart,onDelete:c.deleteTest},null,8,["id","info","data","status","valid","url","openfaasUrl","pid","sid","startMinimized","onRestart","onDelete"])})),128))])}s("b64b"),s("d3b7"),s("e9c4"),s("4de4"),s("4fad");var r=s("864c"),c=["id"],a={class:"card-body"},l={class:"row"},d={class:"col-10 project_name","data-mdb-toggle":"tooltip",title:"Project name"},u=Object(n["h"])("div",{class:"col-1"},[Object(n["h"])("div",{class:"spinner-border text-primary spinner","data-mdb-toggle":"tooltip",title:"Running"})],-1),f={class:"col-1","data-mdb-toggle":"tooltip",title:"Cancel"};function h(t,e,s,o,i,r){return Object(n["v"])(),Object(n["g"])("div",{class:"card project-card",id:s.id},[Object(n["h"])("div",a,[Object(n["h"])("div",l,[Object(n["h"])("div",d," Installing project: "+Object(n["C"])(s.id),1),u,Object(n["h"])("div",f,[Object(n["h"])("i",{class:"fas fa-times stop-install-project",onClick:e[0]||(e[0]=function(){return r.stop&&r.stop.apply(r,arguments)})})])])])],8,c)}var p={name:"InstallationProcess",props:["id","url","openfaasUrl","socket"],data:function(){return{socketIntv:null}},methods:{stop:function(){var t=this;fetch(this.url,{method:"POST",body:JSON.stringify({command:15,project_name:this.id})}).then((function(t){return t.json()})).then((function(e){e.success?(t.$root.showInfo(t.id+": installation canceled successfully","green"),t.$emit("delete")):t.$root.showInfo("There was an error canceling the installation","red")})).catch((function(){t.$root.showInfo("Could not connect to server","red")}))}},beforeUnmount:function(){this.socketIntv&&clearInterval(this.socketIntv)},mounted:function(){var t=this;this.socketIntv=setInterval((function(){t.socket.emit("task_stats",{project_name:t.id,openfaasurl:t.openfaasUrl})}),1e3),this.socket.on(this.id,(function(e){var s=JSON.parse(e.data);s.success?3===s.status_code?console.log("thread is locking"):2===s.status_code?console.log("installing project"):1===s.status_code?(console.log("installing failed"),clearInterval(t.socketIntv),t.$root.showInfo("Installation failed","red",s.error),t.$emit("delete")):(console.log("Task is finished"),clearInterval(t.socketIntv),t.$emit("delete"),t.$root.showInfo("Installation successs","green")):(console.log("Something went wrong"),t.$root.showInfo("Something went wrong","red"),clearInterval(t.socketIntv))}))}},m=s("6b0d"),b=s.n(m);const v=b()(p,[["render",h]]);var j=v,k={name:"Control",components:{Test:r["a"],InstallationProcess:j},props:["url","openfaasUrl","socket","minimizeTests","update"],data:function(){return{tests:{},projects:[]}},methods:{register:function(){var t=this;this.socket.off(this.openfaasUrl+"_control"),this.socket.emit("register_control",{openfaasurl:this.openfaasUrl}),this.socket.on(this.openfaasUrl+"_control",(function(e){if(IsJsonString(e)&&(e=JSON.parse(e),e.success))if(Object.keys(e.tests).length>=Object.keys(t.tests).length)for(var s in e.tests){var n=e.tests[s].id;n in t.tests?(t.tests[n].data=e.tests[s].data,t.tests[n].valid=e.tests[s].valid):t.tests[n]=e.tests[s]}else for(var s in t.tests)if(s in e.tests){var o=e.tests[s].id;o in t.tests?(t.tests[o].data=e.tests[s].data,t.tests[o].valid=e.tests[s].valid):t.tests[o]=e.tests[s]}else t.tests[s].status=0}))},init:function(){var t=this;fetch(this.url,{method:"POST",body:JSON.stringify({command:13})}).then((function(t){return t.json()})).then((function(e){e.success&&(t.tests=e.tests)})).catch((function(){t.$emit("info","Could not connect to server","red")})),fetch(this.url,{method:"POST",body:JSON.stringify({command:1})}).then((function(t){return t.json()})).then((function(e){e.success&&(t.projects=e.projects)})).catch((function(){t.$emit("info","Could not connect to server","red")})),this.register(),this.socket.on(this.openfaasUrl+"_control_test_delete",(function(e){for(var s=0;s<e.length;s++)e[s]in t.tests&&delete t.tests[e[s]]})),this.socket.on(this.openfaasUrl+"_control_test_stop",(function(e){e in t.tests&&(t.tests[e].status=0)}))},killRunningTasks:function(){var t=this;this.$root.setUpConfirmation("Kill all running tasks? Istallation tasks will also be killed","Kill",(function(){fetch(t.url,{method:"POST",body:JSON.stringify({command:911})}).then((function(t){return t.json()})).then((function(e){if(e.success)for(var s in t.$emit("info","Success","green"),t.tests)t.tests[s].status=0;else t.$emit("info","There was an error killing running tasks","red")})).catch((function(){t.$emit("info","Could not connect to server","red")}))}))},deleteAllProjects:function(){var t=this;this.$root.setUpConfirmation("Delete all projects?","Delete",(function(){fetch(t.url,{method:"POST",body:JSON.stringify({command:912})}).then((function(t){return t.json()})).then((function(e){e.success?(t.$emit("info","Success","green"),t.tests={}):t.$emit("info","There was an error deleting projects","red")})).catch((function(){t.$emit("info","Could not connect to server","red")}))}))},restart:function(t,e,s){this.start(t.users,t.spawn_rate,t.workers,t.host,t.time,e,s)},start:function(t,e,s,n,o,i,r){var c=this;fetch(this.url,{method:"POST",body:JSON.stringify({command:5,project_name:i,script_name:r,users:parseInt(t),spawn_rate:parseInt(e),workers:parseInt(s),host:n,time:parseInt(o)})}).then((function(t){return t.json()})).then((function(a){if(a.success){var l=a.id,d=a.started_at,u=JSON.stringify({users:t,spawn_rate:e,host:n,workers:s,time:o,started_at:d}),f=1,h=!0,p={id:l,info:u,status:f,valid:h,project_name:i,script_name:r,data:JSON.stringify([])};c.tests[l]=p,c.socket.emit("test_start",{openfaasurl:c.openfaasUrl,project_name:i,script_name:r,test:p})}})).catch((function(){c.$emit("info","Could not connect to server","red")}))},deleteTest:function(t,e,s){delete this.tests[t],this.socket.emit("test_delete",{openfaasurl:this.openfaasUrl,project_name:e,script_name:s,ids:[t]})},deleteProject:function(t){this.projects=this.projects.filter((function(e){return e!==t}))}},computed:{reversedTests:function(){return Object.entries(this.tests).reverse()}},beforeUnmount:function(){this.socket.emit("disconnect_control"),this.socket.off(this.openfaasUrl+"_control"),this.socket.off(this.openfaasUrl+"_control_test_delete"),this.socket.off(this.openfaasUrl+"_control_test_stop")},mounted:function(){this.init()},updated:function(){this.update&&(this.init(),this.$root.updated())}};const g=b()(k,[["render",i]]);e["default"]=g}}]);
//# sourceMappingURL=chunk-2d0a43a1.e5df643f.js.map