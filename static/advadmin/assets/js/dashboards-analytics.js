/**
 * Dashboard Analytics (with per-year growth progress radial bar, percent and count)
 */
'use strict';

(function () {
    // --- Color setup ---
    let cardColor = config.colors.white;
    let headingColor = config.colors.headingColor;
    let axisColor = config.colors.axisColor;
    let borderColor = config.colors.borderColor;
    let shadeColor = config.colors.shadeColor;

    // --- Data from Django/Template JS ---
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var trends = window.membershipTrends || {};
    var revenueData = window.monthlyRevenue || {};
    var years = window.allYears || [window.currentYear, window.currentYear - 1];
    var selectedYear = window.currentYear || new Date().getFullYear();

    function getTrendSeries(year) {
        return [{
            name: String(year),
            data: trends[year] || new Array(12).fill(0)
        }];
    }
    function getRevenueSeries(year) {
        return [{
            name: "Revenue",
            data: revenueData[year] || new Array(12).fill(0)
        }];
    }

    // --- Total Revenue Bar Chart ---
    const totalRevenueChartEl = document.querySelector('#totalRevenueChart');
    const totalRevenueChartOptions = {
        series: getTrendSeries(selectedYear),
        chart: {
            height: 300,
            stacked: true,
            type: 'bar',
            toolbar: { show: false }
        },
        plotOptions: {
            bar: { horizontal: false, columnWidth: '33%', borderRadius: 12, startingShape: 'rounded', endingShape: 'rounded' }
        },
        colors: [config.colors.primary],
        dataLabels: { enabled: false },
        stroke: {
            curve: 'smooth',
            width: 6,
            lineCap: 'round',
            colors: [cardColor]
        },
        legend: {
            show: true,
            horizontalAlign: 'left',
            position: 'top',
            markers: { height: 8, width: 8, radius: 12, offsetX: -3 },
            labels: { colors: axisColor },
            itemMargin: { horizontal: 10 }
        },
        grid: { borderColor: borderColor, padding: { top: 0, bottom: -8, left: 20, right: 20 }},
        xaxis: {
            categories: months,
            labels: { style: { fontSize: '13px', colors: axisColor } },
            axisTicks: { show: false }, axisBorder: { show: false }
        },
        yaxis: { labels: { style: { fontSize: '13px', colors: axisColor } } },
        responsive: [
            { breakpoint: 1700, options: { plotOptions: { bar: { borderRadius: 10, columnWidth: '32%' }}} },
            { breakpoint: 1580, options: { plotOptions: { bar: { borderRadius: 10, columnWidth: '35%' }}} },
            { breakpoint: 1440, options: { plotOptions: { bar: { borderRadius: 10, columnWidth: '42%' }}} },
            { breakpoint: 1300, options: { plotOptions: { bar: { borderRadius: 10, columnWidth: '48%' }}} },
            { breakpoint: 1200, options: { plotOptions: { bar: { borderRadius: 10, columnWidth: '40%' }}} },
            { breakpoint: 1040, options: { plotOptions: { bar: { borderRadius: 11, columnWidth: '48%' }}} },
            { breakpoint: 991, options: { plotOptions: { bar: { borderRadius: 10, columnWidth: '30%' }}} },
            { breakpoint: 840, options: { plotOptions: { bar: { borderRadius: 10, columnWidth: '35%' }}} },
            { breakpoint: 768, options: { plotOptions: { bar: { borderRadius: 10, columnWidth: '28%' }}} },
            { breakpoint: 640, options: { plotOptions: { bar: { borderRadius: 10, columnWidth: '32%' }}} },
            { breakpoint: 576, options: { plotOptions: { bar: { borderRadius: 10, columnWidth: '37%' }}} },
            { breakpoint: 480, options: { plotOptions: { bar: { borderRadius: 10, columnWidth: '45%' }}} },
            { breakpoint: 420, options: { plotOptions: { bar: { borderRadius: 10, columnWidth: '52%' }}} },
            { breakpoint: 380, options: { plotOptions: { bar: { borderRadius: 10, columnWidth: '60%' }}} }
        ],
        states: { hover: { filter: { type: 'none' } }, active: { filter: { type: 'none' } } }
    };
    if (totalRevenueChartEl) {
        window.totalRevenueChart = new ApexCharts(totalRevenueChartEl, totalRevenueChartOptions);
        window.totalRevenueChart.render();
    }

    // --- Year selection for all widgets ---
    document.querySelectorAll('.year-select').forEach(function (item) {
        item.addEventListener('click', function () {
            let year = parseInt(this.getAttribute('data-year'), 10);
            let lastYear = year - 1;
            // Update year button text
            var growthReportBtn = document.getElementById('growthReportId');
            if (growthReportBtn) growthReportBtn.innerText = year;
            // Earnings update
            var thisYearEarningEl = document.getElementById('thisYearEarning');
            var thisYearLabelEl = document.getElementById('thisYearLabel');
            var lastYearEarningEl = document.getElementById('lastYearEarning');
            var lastYearLabelEl = document.getElementById('lastYearLabel');
            if (thisYearEarningEl) {
                var thisYearAmount = window.yearlyEarnings[year] || 0;
                thisYearEarningEl.innerText = '₹' + thisYearAmount.toLocaleString(undefined, {minimumFractionDigits: 2});
            }
            if (thisYearLabelEl) thisYearLabelEl.innerText = year;
            if (lastYearEarningEl) {
                var lastYearAmount = window.yearlyEarnings[lastYear] || 0;
                lastYearEarningEl.innerText = '₹' + lastYearAmount.toLocaleString(undefined, {minimumFractionDigits: 2});
            }
            if (lastYearLabelEl) lastYearLabelEl.innerText = lastYear;
            // Charts update
            renderGrowthRadialBar(year);
            let newSeries = getTrendSeries(year);
            if (window.totalRevenueChart)
                window.totalRevenueChart.updateSeries(newSeries);
            let incomeSeries = getRevenueSeries(year);
            if (window.incomeChart)
                window.incomeChart.updateSeries(incomeSeries);
        });
    });

    // --- Growth/Decline Radial Chart ---
    let growthData = (window.growthYearData || {});
    let growthRadialChart = null;

    function renderGrowthRadialBar(key) {
        console.log("Selected key:", key);
        let yd = growthData[key] || { percent: 0, count: 0 };
        let percent = Math.abs(yd.percent || 0);
        let count = yd.count || 0;
        let isDecline = (yd.percent || 0) < 0;

        // Make sure these config colors are defined somewhere globally
        let color = isDecline ? "#e53935" : (config.colors.primary || "#007bff");
        let cardColor = config.cardColor || "#f8f9fa";   // fallback example
        let headingColor = config.headingColor || "#343a40"; // fallback example

        let label = isDecline ? "Decline" : "Growth";
        let suffix = "%";
        let sign = (yd.percent > 0) ? "+" : (yd.percent < 0 ? "-" : "");
        let display = sign + percent + suffix + " (" + count + ")";

        const options = {
            series: [percent],
            labels: [label],
            chart: {
                height: 240,
                type: 'radialBar',
                animations: { enabled: true }
            },
            plotOptions: {
                radialBar: {
                    size: 150,
                    offsetY: 10,
                    startAngle: -150,
                    endAngle: 150,
                    hollow: { size: '55%' },
                    track: { background: cardColor, strokeWidth: '100%' },
                    dataLabels: {
                        name: {
                            offsetY: 15,
                            color: headingColor,
                            fontSize: '15px',
                            fontWeight: 600,
                            fontFamily: 'Public Sans'
                        },
                        value: {
                            offsetY: -25,
                            color: headingColor,
                            fontSize: '22px',
                            fontWeight: 500,
                            fontFamily: 'Public Sans',
                            formatter: function() { return display; }
                        }
                    }
                }
            },
            colors: [color],
            fill: {
                type: 'gradient',
                gradient: {
                    shade: 'dark',
                    shadeIntensity: 0.5,
                    gradientToColors: [color],
                    inverseColors: true,
                    opacityFrom: 1,
                    opacityTo: 0.6,
                    stops: [30, 70, 100]
                }
            },
            stroke: { dashArray: 5 }
        };

        const chartElem = document.getElementById("growthChart");
        if (!chartElem) return;

        if (!growthRadialChart) {
            growthRadialChart = new ApexCharts(chartElem, options);
            growthRadialChart.render();
            window.growthRadialChart = growthRadialChart;
        } else {
            growthRadialChart.updateOptions({
                series: [percent],
                labels: [label],
                colors: [color],
                fill: options.fill,
                plotOptions: options.plotOptions
            });
        }

        const labelElem = document.getElementById("growthChartLabel");
        if (labelElem) {
            labelElem.innerText = key + ": " + display + " members";
        }
    }

    // Dropdown menu event listener to change the chart data when a month is selected
    document.getElementById('growthDropdownMenu').addEventListener('click', function(e) {
        let target = e.target;
        if (target.matches('a.dropdown-item')) {
            e.preventDefault();
            let key = target.getAttribute('data-key');
            if (key && window.growthYearData[key]) {
                renderGrowthRadialBar(key);
                document.getElementById('growthReportId').textContent = key;
            }
        }
    });

    // Initialize the chart with the latest month key on page load
    let monthKeys = Object.keys(growthData);
    let latestMonthKey = monthKeys.length ? monthKeys[monthKeys.length - 1] : null;

    if (latestMonthKey) {
        renderGrowthRadialBar(latestMonthKey);
    }


    // --- Profit Report Line Chart ---
    const profileReportChartEl = document.querySelector('#profileReportChart'),
        profileReportChartConfig = {
            chart: {
                height: 80,
                type: 'line',
                toolbar: { show: false },
                dropShadow: {
                    enabled: true,
                    top: 10,
                    left: 5,
                    blur: 3,
                    color: config.colors.warning,
                    opacity: 0.15
                },
                sparkline: { enabled: true }
            },
            grid: { show: false, padding: { right: 8 } },
            colors: [config.colors.warning],
            dataLabels: { enabled: false },
            stroke: { width: 5, curve: 'smooth' },
            series: [{ data: [110, 270, 145, 245, 205, 285] }],
            xaxis: { show: false, lines: { show: false }, labels: { show: false }, axisBorder: { show: false } },
            yaxis: { show: false }
        };
    if (profileReportChartEl) {
        const profileReportChart = new ApexCharts(profileReportChartEl, profileReportChartConfig);
        profileReportChart.render();
    }

    // --- Order Statistics Chart ---
    const chartOrderStatistics = document.querySelector('#orderStatisticsChart'),
        orderChartConfig = {
            chart: { height: 165, width: 130, type: 'donut' },
            labels: orderStatsData.labels,
            series: orderStatsData.series,
            colors: [
                config.colors.primary,
                config.colors.secondary,
                config.colors.info,
                config.colors.success
            ],
            stroke: { width: 5, colors: cardColor },
            dataLabels: {
                enabled: false,
                formatter: function (val, opt) { return parseInt(val) + '%'; }
            },
            legend: { show: false },
            grid: { padding: { top: 0, bottom: 0, right: 15 } },
            plotOptions: {
                pie: {
                    donut: {
                        size: '75%',
                        labels: {
                            show: true,
                            value: {
                                fontSize: '1.5rem',
                                fontFamily: 'Public Sans',
                                color: headingColor,
                                offsetY: -15,
                                formatter: function (val) { return parseInt(val) + '%'; }
                            },
                            name: { offsetY: 20, fontFamily: 'Public Sans' },
                            total: {
                                show: true,
                                fontSize: '0.8125rem',
                                color: axisColor,
                                label: 'Weekly',
                                formatter: function () { return '38%'; }
                            }
                        }
                    }
                }
            }
        };
    if (chartOrderStatistics) {
        const statisticsChart = new ApexCharts(chartOrderStatistics, orderChartConfig);
        statisticsChart.render();
    }

    // --- Income Chart - Area chart ---
    const incomeChartEl = document.querySelector('#incomeChart'),
        incomeChartConfig = {
            series: getRevenueSeries(selectedYear),
            chart: { height: 215, parentHeightOffset: 0, parentWidthOffset: 0, toolbar: { show: false }, type: 'area' },
            dataLabels: { enabled: false },
            stroke: { width: 2, curve: 'smooth' },
            legend: { show: false },
            markers: { size: 6, colors: 'transparent', strokeColors: 'transparent', strokeWidth: 4, discrete: [], hover: { size: 7 }},
            colors: [config.colors.primary],
            fill: {
                type: 'gradient',
                gradient: { shade: shadeColor, shadeIntensity: 0.6, opacityFrom: 0.5, opacityTo: 0.25, stops: [0, 95, 100] }
            },
            grid: { borderColor: borderColor, strokeDashArray: 3, padding: { top: -20, bottom: -8, left: -10, right: 8 }},
            xaxis: { categories: months, axisBorder: { show: false }, axisTicks: { show: false }, labels: { show: true, style: { fontSize: '13px', colors: axisColor } } },
            yaxis: { labels: { show: true, style: { fontSize: '13px', colors: axisColor } }, min: 0 }
        };
    if (incomeChartEl) {
        window.incomeChart = new ApexCharts(incomeChartEl, incomeChartConfig);
        window.incomeChart.render();
    }

    // --- Expenses Mini Chart ---
    const weeklyExpensesEl = document.querySelector('#expensesOfWeek'),
        weeklyExpensesConfig = {
            series: [65],
            chart: { width: 60, height: 60, type: 'radialBar' },
            plotOptions: {
                radialBar: {
                    startAngle: 0,
                    endAngle: 360,
                    strokeWidth: '8',
                    hollow: { margin: 2, size: '45%' },
                    track: { strokeWidth: '50%', background: borderColor },
                    dataLabels: {
                        show: true,
                        name: { show: false },
                        value: {
                            formatter: function (val) { return '$' + parseInt(val); },
                            offsetY: 5,
                            color: '#697a8d',
                            fontSize: '13px',
                            show: true
                        }
                    }
                }
            },
            fill: { type: 'solid', colors: config.colors.primary },
            stroke: { lineCap: 'round' },
            grid: { padding: { top: -10, bottom: -15, left: -10, right: -10 } },
            states: { hover: { filter: { type: 'none' } }, active: { filter: { type: 'none' } } }
        };
    if (weeklyExpensesEl) {
        const weeklyExpenses = new ApexCharts(weeklyExpensesEl, weeklyExpensesConfig);
        weeklyExpenses.render();
    }
})();
