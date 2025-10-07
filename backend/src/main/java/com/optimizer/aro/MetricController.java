package com.optimizer.aro;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
@RestController
@RequestMapping("/api/metrics")
public class MetricController {
    private final MetricRepository metricRepository;

    public MetricController(MetricRepository metricRepository) {
        this.metricRepository = metricRepository;
    }

    @PostMapping
    public Metric createMetric(@RequestBody Metric metric) {
        metric.setTimestamp(Instant.now());
        return metricRepository.save(metric);
    }

    @GetMapping
    public Page<Metric> getAllMetrics(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "100") int size,
            @RequestParam(defaultValue = "timestamp,desc") String[] sort) {

        String sortField = sort[0];
        Sort.Direction direction = sort.length > 1 && sort[1].equalsIgnoreCase("desc") ?
                Sort.Direction.DESC : Sort.Direction.ASC;

        Pageable pageable = PageRequest.of(page, size, Sort.by(direction, sortField));

        return metricRepository.findAll(pageable);
    }


}
