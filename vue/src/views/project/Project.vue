<template>
  <div>
    <h3>{{ id }}</h3>
    <div class="list-group">
      <a
        v-for="script in scripts"
        :key="script"
        :id="script"
        @click="navigateToScript(script)"
        class="list-group-item list-group-item-action"
      >
        <router-link :to="{ name: 'Script', params: { pid: id, id: script } }">
          <label class="test-label"> {{ script }} </label>
        </router-link>
      </a>
    </div>
  </div>
</template>

<script>
export default {
  name: "Project",
  props: ["url", "openfaasUrl", "socket", "update"],
  data() {
    return {
      id: this.$route.params.id,
      scripts: [],
    };
  },
  methods: {
    init() {
      fetch(this.url, {
        method: "POST",
        body: JSON.stringify({ command: 4, project_name: this.id }),
      })
        .then((data) => data.json())
        .then((data) => {
          if (data.success) {
            this.scripts = data.locust_scripts;
          }
        })
        .catch(() => {
          this.$emit("info", "Could not connect to server", "red");
        });
    },
    navigateToScript(script) {
      this.$router.push({
        name: "Script",
        params: { pid: this.id, id: script },
      });
    },
  },
  mounted() {
    this.init();
  },
  updated() {
    if (this.update) {
      this.init();
      this.$root.updated();
    }
  },
};
</script>

<style>
</style>