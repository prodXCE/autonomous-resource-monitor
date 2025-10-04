package com.optimizer.aro;

import org.springframework.data.repository.PagingAndSortingRepository;

public interface MetricRepository extends PagingAndSortingRepository<Metric, Long> {

    Metric save(Metric metric);
}