<template>
  <div class="chart-container">
    <BarChart :chart-data="chartData" :chart-options="chartOptions" />
  </div>
</template>

<script>
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';
import { BarChart } from 'vue-chartjs';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

export default {
  name: 'DashboardChart',
  components: { BarChart },
  props: {
    stats: {
      type: Object,
      required: true
    }
  },
  computed: {
    chartData() {
      return {
        labels: ['Registered Vendors', 'Approved Vendors', 'Total Products'],
        datasets: [
          {
            label: 'Statistics',
            backgroundColor: ['#2563EB', '#059669', '#8B5CF6'],
            data: [this.stats.registered, this.stats.approved, this.stats.products]
          }
        ]
      };
    },
    chartOptions() {
      return {
        responsive: true,
        plugins: {
          legend: { display: false },
          title: { display: true, text: 'Admin Dashboard Overview', font: { size: 18 } }
        },
        scales: {
          y: { beginAtZero: true }
        }
      };
    }
  }
};
</script>

<style scoped>
.chart-container {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0,0,0,.05);
  margin-bottom: 20px;
}
</style>
