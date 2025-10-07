package com.optimizer.aro;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/anomalies")
public class AnomalyController {

    // This counter is the custom prometheus metric
    private final Counter anomalyCounter;

    public AnomalyController(MeterRegistry registry) {
        this.anomalyCounter = Counter.builder("aro_anomalies_detected_total")
            .description("Total number of anomalies detected by the ML worker.")
            .register(registry);
    }

    @PostMapping("/report")
    public void reportAnomaly() {
        this.anomalyCounter.increment();
        System.out.println("ANOMALY REPORT: Incrementing aro_anomalies_detected_total counter.");
    }

}
