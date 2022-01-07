<template>
  <div>
    <div class="btn-container">
      <button
        type="button"
        class="btn btn-primary"
        data-mdb-toggle="modal"
        data-mdb-target="#Modal"
        id="add-btn-Modal"
        :disabled="loading"
      >
        Add a new project
      </button>
      <button
        type="button"
        class="btn btn-danger"
        id="delete-project"
        :disabled="!enableDelete"
        @click="deleteProjects"
      >
        Delete
      </button>
    </div>
    <div class="list-group">
      <a
        v-for="project in projects"
        :key="project"
        class="list-group-item list-group-item-action"
        @click="navigateToProject(project)"
      >
        <div class="form-check">
          <input
            class="form-check-input"
            type="checkbox"
            :value="project"
            v-model="markedProjects"
            :id="project"
            @click.stop="stopTheEvent"
          />
          <router-link :to="{ name: 'Project', params: { id: project } }">
            <label class="test-label">{{ project }}</label>
          </router-link>
        </div>
      </a>
    </div>
    <!-- Modal -->
    <div
      class="modal fade"
      id="Modal"
      tabindex="-1"
      aria-labelledby="ModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="ModalLabel">Add a new Project</h5>
          </div>
          <div class="modal-body">
            <form>
              <div class="form-outline mb-4">
                <input
                  type="file"
                  webkitdirectory
                  mozdirectory
                  id="project-input"
                  ref="files"
                />
              </div>
              <div v-if="uploading" class="btn-container">
                <div class="spinner-border text-primary spinner"></div>
              </div>
              <div class="upload-message" v-if="!uploading">
                Please make sure all names don't include blank spaces
              </div>
              <!-- Submit button -->
              <button
                type="button"
                class="btn btn-primary btn-block"
                id="add-btn"
                @click="upload"
                v-if="!uploading"
              >
                Add
              </button>
            </form>
            <button
              type="button"
              class="btn btn-primary hidden"
              data-mdb-dismiss="modal"
              id="dismiss-btn"
              ref="dismissBtn"
            ></button>
          </div>
        </div>
      </div>
    </div>
    <div class="btn-container">
      <div
        v-if="loading"
        class="spinner-border text-primary spinner"
        id="spinner"
      ></div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Home",
  props: ["url", "openfaasUrl", "socket", "update"],
  data() {
    return {
      projects: [],
      loading: false,
      files: null,
      socketIntv: null,
      markedProjects: [],
      projectId: "",
      uploading: false,
    };
  },
  methods: {
    init() {
      fetch(this.url, { method: "POST", body: JSON.stringify({ command: 3 }) })
        .then((data) => data.json())
        .then((data) => {
          if (data.success) {
            this.projects = data.projects;
            //console.log(data);
          } else {
            this.$emit("info", "Could not connect to server", "red");
          }
        })
        .catch(() => {
          this.$emit("info", "Could not connect to server", "red");
        });
      this.socket.on(this.openfaasUrl + "_project_upload", (msg) => {
        this.projects.push(msg);
      });
      this.socket.on(this.openfaasUrl + "_project_delete", (msg) => {
        this.projects = this.projects.filter(
          (project) => !msg.includes(project)
        );
      });
    },
    upload() {
      const files = this.$refs.files.files;
      if (files.length < 1) {
        this.$emit("info", "Please select a directory to upload", "red");
        return false;
      }
      var data = new FormData();
      for (var i = 0; i < files.length; i++) {
        data.append("file" + i, files[i]);
      }
      this.uploading = true;
      fetch(this.url, { method: "POST", body: data })
        .then((data) => data.json())
        .then((data) => {
          this.uploading = false;

          this.$refs.dismissBtn.click();
          //console.log(data);
          if (data.success) {
            this.loading = true;
            this.projectId = data.task_id;
            this.socketIntv = setInterval(() => {
              this.socket.emit("task_stats", {
                project_name: this.projectId,
                openfaasurl: this.openfaasUrl,
              });
            }, 1000);
            this.socket.on(this.projectId, (message) => {
              //console.log(message);
              const data = JSON.parse(message.data);
              if (!data.success) {
                //console.log("Something went wrong");
                this.loading = false;
                this.$emit("info", "Something went wrong", "red");
                clearInterval(this.socketIntv);
              } else if (data.status_code === 3) {
                //console.log("thread is locking");
              } else if (data.status_code === 2) {
                //console.log("installing project");
              } else if (data.status_code === 1) {
                //console.log("installing failed");
                clearInterval(this.socketIntv);
                this.loading = false;
                this.$emit("info", "Installation failed", "red", data.error);
              } else {
                //console.log("Task is finished");
                clearInterval(this.socketIntv);
                this.$router.push({
                  name: "Project",
                  params: { id: this.projectId },
                });
                this.socket.emit("project_upload", {
                  openfaasurl: this.openfaasUrl,
                  project_name: this.projectId,
                });
              }
            });
          } else {
            this.uploading = false;
            this.loading = false;
            this.$emit("info", data.message, "red");
          }
        })
        .catch(() => {
          this.$refs.dismissBtn.click();
          this.uploading = false;
          this.loading = false;
          this.$emit("info", "Something went wrong", "red");
        });
      return false;
    },
    deleteProjects() {
      this.$root.setUpConfirmation(
        "Are you sure you want to delete these projects?",
        "Delete",
        () => {
          fetch(this.url, {
            method: "POST",
            body: JSON.stringify({ command: 10, names: this.markedProjects }),
          })
            .then((data) => data.json())
            .then((data) => {
              if (data.success) {
                this.socket.emit("project_delete", {
                  openfaasurl: this.openfaasUrl,
                  project_names: this.markedProjects,
                });
                this.projects = this.projects.filter(
                  (project) => !this.markedProjects.includes(project)
                );
                this.markedProjects = [];
              }else{
                this.$emit("info", data.message, "red");
              }
            })
            .catch(() => {
              this.$emit("info", "Could not connect to server", "red");
            });
          return false;
        }
      );
    },
    navigateToProject(project) {
      this.$router.push({ name: "Project", params: { id: project } });
    },
    freeSocket() {
      this.socket.off(this.projectId);
      this.socket.off(this.openfaasUrl + "_project_upload");
      this.socket.off(this.openfaasUrl + "_project_delete");
      if (this.socketIntv) clearInterval(this.socketIntv);
    },
    stopTheEvent(event) {
      event.stopPropagation();
    },
  },
  computed: {
    enableDelete() {
      return this.markedProjects.length > 0;
    },
  },
  beforeUnmount() {
    this.freeSocket();
  },
  mounted() {
    this.init();
  },
  updated() {
    if (this.update) {
      this.init();
      this.freeSocket();
      this.$root.updated();
    }
  },
};
</script>
