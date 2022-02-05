<template>
  <div
    class="card"
    :class="{
      'no-width': mobileAgent,
    }"
  >
    <div class="card-body">
      <h3 class="card-title">{{ script }}</h3>
      <br/>
      <p v-for="line in out" :key="line">
        {{ line }}
      </p>
    </div>
  </div>
</template>

<script>
export default {
  props: ["out", "script"],
};
</script>

<style>
</style>