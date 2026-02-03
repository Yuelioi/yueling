"""
任务执行引擎 - 处理并发、状态管理、超时等
"""
import asyncio
import time
from typing import Awaitable, Callable, Optional, TypeVar, Generic

from nonebot import logger

from .exceptions import BackupStateException, TaskExecutionException
from .models_domain import TaskResult

T = TypeVar("T", bound=TaskResult)


class TaskExecutor(Generic[T]):  
    """任务执行器 - 管理任务的生命周期和状态"""
    
    def __init__(self, group_id: int):
        self.group_id = group_id
        self._is_processing = False
        self._start_time: Optional[float] = None
        self._current_result: Optional[TaskResult] = None
        self._lock = asyncio.Lock()
    
    @property
    def is_processing(self) -> bool:
        """是否正在处理任务"""
        return self._is_processing
    
    @property
    def duration(self) -> float:
        """任务耗时（秒）"""
        if self._start_time is None:
            return 0.0
        return round(time.time() - self._start_time, 2)
    
    async def acquire(self) -> None:
        """获取执行权 - 线程安全"""
        async with self._lock:
            if self._is_processing:
                raise BackupStateException(
                    f"群 {self.group_id} 已有任务在执行中，请稍候"
                )
            self._is_processing = True
            self._start_time = time.time()
    
    async def release(self) -> None:
        """释放执行权"""
        async with self._lock:
            self._is_processing = False
    
    async def execute(
        self,
        task_func: Callable[...,  Awaitable[T]],
        task_name: str,
        *args,
        **kwargs
    ) -> T:
        """
        执行任务
        
        Args:
            task_func: 异步任务函数，必须返回 TaskResult 子类
            task_name: 任务名称（用于日志）
            *args, **kwargs: 传递给task_func的参数
        
        Returns:
            T: 任务结果（具体的Result类型）
        """
        try:
            await self.acquire()
            logger.info(f"[{self.group_id}] 开始任务: {task_name}")
            
            result: T = await task_func(*args, **kwargs) 
            
            # 更新执行时间
            result.duration = self.duration
            logger.info(
                f"[{self.group_id}] 任务完成: {task_name} "
                f"(成功: {result.success_count}, 失败: {len(result.failed_files)}, "
                f"耗时: {result.duration}s)"
            )
            return result
            
        except Exception as e:
            logger.error(f"[{self.group_id}] 任务失败: {task_name}, 错误: {e}", exc_info=True)
            raise 
        
        finally:
            await self.release()
    
    async def execute_with_concurrency(
        self,
        tasks: list,
        max_workers: int = 3,
        task_name: str = "并发任务"
    ) -> tuple[list, list]:
        """
        执行并发任务
        
        Args:
            tasks: 任务列表（协程对象）
            max_workers: 最大并发数
            task_name: 任务名称
        
        Returns:
            (成功结果列表, 失败任务列表)
        """
        if not tasks:
            return [], []
        
        logger.info(
            f"[{self.group_id}] 开始执行 {len(tasks)} 个{task_name}，"
            f"最大并发数: {max_workers}"
        )
        
        semaphore = asyncio.Semaphore(max_workers)
        
        async def bounded_task(task):
            async with semaphore:
                try:
                    return await task, None
                except Exception as e:
                    return None, e
        
        results = await asyncio.gather(
            *(bounded_task(task) for task in tasks),
            return_exceptions=False
        )
        
        successes = [r[0] for r in results if r[0] is not None]
        failures = [r[1] for r in results if r[1] is not None]
        
        return successes, failures


# 每个群一个执行器
_executors: dict[int, TaskExecutor] = {}


def get_executor(group_id: int) -> TaskExecutor:
    """获取或创建执行器"""
    if group_id not in _executors:
        _executors[group_id] = TaskExecutor(group_id)
    return _executors[group_id]