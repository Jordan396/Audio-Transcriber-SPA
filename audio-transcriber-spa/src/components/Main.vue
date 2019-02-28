<template>
  <div>
    <section class="hero is-primary">
      <div class="hero-body">
        <div class="container has-text-centered">
          <h2 class="title">Simple Audio Transcriber</h2>
        </div>
      </div>
    </section>
    <div class="container is-fluid" id="main-container">
      <div class="notification">
        <div v-if="submitted">
          <AudioTranscriberUnsubmitted v-on:toggle-component="toggleSubmitted"></AudioTranscriberUnsubmitted>
        </div>
        <div v-else>
          <AudioTranscriberSubmitted/>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
#main-container {
  padding-top: 100px;
}
</style>

<script>
import AudioTranscriberUnsubmitted from "./AudioTranscriberUnsubmitted";
import AudioTranscriberSubmitted from "./AudioTranscriberSubmitted";
export default {
  name: "Main",
  data: function() {
    return {
      submitted: true
    };
  },
  components: {
    AudioTranscriberUnsubmitted: AudioTranscriberUnsubmitted,
    AudioTranscriberSubmitted: AudioTranscriberSubmitted
  },
  methods: {
    toggleSubmitted() {
      this.$data.submitted = false;
    }
  }
};
</script>
