<template>
  <div class="app-container">
    <!-- 搜索区域 -->
    <div v-show="visible" class="search-container">
      <el-form ref="queryFormRef" :model="queryFormData" label-suffix=":" :inline="true" @submit.prevent="handleQuery">
        <el-form-item label="名称" prop="name">
          <el-input v-model="queryFormData.name" placeholder="请输入名称" clearable />
        </el-form-item>
        <el-form-item label="UUID全局唯一标识" prop="uuid">
          <el-input v-model="queryFormData.uuid" placeholder="请输入UUID全局唯一标识" clearable />
        </el-form-item>
        <el-form-item label="是否启用(0:启用 1:禁用)" prop="status">
          <el-input v-model="queryFormData.status" placeholder="请输入是否启用(0:启用 1:禁用)" clearable />
        </el-form-item>
        <el-form-item label="创建人ID" prop="created_id">
          <el-input v-model="queryFormData.created_id" placeholder="请输入创建人ID" clearable />
        </el-form-item>
        <el-form-item label="更新人ID" prop="updated_id">
          <el-input v-model="queryFormData.updated_id" placeholder="请输入更新人ID" clearable />
        </el-form-item>
        <!-- 可选：创建人选择与统一日期范围（展开后显示） -->
        <el-form-item v-if="isExpand" prop="creator" label="创建人">
          <UserTableSelect v-model="queryFormData.creator" @confirm-click="handleConfirm" @clear-click="handleQuery" />
        </el-form-item>
        <el-form-item v-if="isExpand" prop="start_time" label="创建时间">
          <DatePicker v-model="dateRange" @update:model-value="handleDateRangeChange" />
        </el-form-item>
        <el-form-item>
          <el-button v-hasPerm="['module_gencode:gen_demo:query']" type="primary" icon="search" @click="handleQuery">查询</el-button>
          <el-button v-hasPerm="['module_gencode:gen_demo:query']" icon="refresh" @click="handleResetQuery">重置</el-button>
          <template v-if="isExpandable">
            <el-link class="ml-3" type="primary" underline="never" @click="isExpand = !isExpand">
            {{ isExpand ? "收起" : "展开" }}
              <el-icon>
                <template v-if="isExpand">
                  <ArrowUp />
                </template>
                <template v-else>
                  <ArrowDown />
                </template>
              </el-icon>
            </el-link>
          </template>
        </el-form-item>
      </el-form>
    </div>

    <!-- 内容区域 -->
    <el-card shadow="hover" class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            <el-tooltip content="示例列表">
              <QuestionFilled class="w-4 h-4 mx-1" />
            </el-tooltip>
            示例列表
          </span>
        </div>
      </template>

      <!-- 功能区域 -->
      <div class="data-table__toolbar">
        <div class="data-table__toolbar--left">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-button v-hasPerm="['module_gencode:gen_demo:create']" type="success" icon="plus" @click="handleOpenDialog('create')">新增</el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button v-hasPerm="['module_gencode:gen_demo:delete']" type="danger" icon="delete" :disabled="selectIds.length === 0" @click="handleDelete(selectIds)">批量删除</el-button>
            </el-col>
            <el-col :span="1.5">
              <el-dropdown v-hasPerm="['module_gencode:gen_demo:batch']" trigger="click">
                <el-button type="default" :disabled="selectIds.length === 0" icon="ArrowDown">更多</el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item icon="Check" @click="handleMoreClick(true)">批量启用</el-dropdown-item>
                    <el-dropdown-item icon="CircleClose" @click="handleMoreClick(false)">批量停用</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </el-col>
          </el-row>
        </div>
        <div class="data-table__toolbar--right">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-tooltip content="导入">
                <el-button v-hasPerm="['module_gencode:gen_demo:import']" type="success" icon="upload" circle @click="handleOpenImportDialog" />
              </el-tooltip>
            </el-col>
            <el-col :span="1.5">
              <el-tooltip content="导出">
                <el-button v-hasPerm="['module_gencode:gen_demo:export']" type="warning" icon="download" circle @click="handleOpenExportsModal" />
              </el-tooltip>
            </el-col>
            <el-col :span="1.5">
              <el-tooltip content="搜索显示/隐藏">
                <el-button v-hasPerm="['*:*:*']" type="info" icon="search" circle @click="visible = !visible" />
              </el-tooltip>
            </el-col>
            <el-col :span="1.5">
              <el-tooltip content="刷新">
                <el-button v-hasPerm="['module_gencode:gen_demo:refresh']" type="primary" icon="refresh" circle @click="handleRefresh" />
              </el-tooltip>
            </el-col>
            <el-col :span="1.5">
              <el-popover placement="bottom" trigger="click">
                <template #reference>
                  <el-button type="danger" icon="operation" circle></el-button>
                </template>
                <el-scrollbar max-height="350px">
                  <template v-for="column in tableColumns" :key="column.prop">
                    <el-checkbox v-if="column.prop" v-model="column.show" :label="column.label" />
                  </template>
                </el-scrollbar>
              </el-popover>
            </el-col>
          </el-row>
        </div>
      </div>

      <!-- 表格区域 -->
      <el-table
        ref="dataTableRef"
        v-loading="loading"
        :data="pageTableData"
        highlight-current-row
        class="data-table__content"
        :height="450"
        border
        stripe
        @selection-change="handleSelectionChange"
      >
        <template #empty>
          <el-empty :image-size="80" description="暂无数据" />
        </template>
        <el-table-column v-if="tableColumns.find((col) => col.prop === 'selection')?.show" type="selection" min-width="55" align="center" />
        <el-table-column v-if="tableColumns.find((col) => col.prop === 'index')?.show" fixed label="序号" min-width="60">
          <template #default="scope">
           {{ (queryFormData.page_no - 1) * queryFormData.page_size + scope.$index + 1 }}
          </template>
        </el-table-column>
        <el-table-column v-if="tableColumns.find((col) => col.prop === 'name')?.show" label="名称" prop="name" min-width="140">
        </el-table-column>
        <el-table-column v-if="tableColumns.find((col) => col.prop === 'uuid')?.show" label="UUID全局唯一标识" prop="uuid" min-width="140">
        </el-table-column>
        <el-table-column v-if="tableColumns.find((col) => col.prop === 'status')?.show" label="是否启用(0:启用 1:禁用)" prop="status" min-width="140">
          <template #default="scope">
            <el-tag :type="scope.row.status ? 'success' : 'info'">{{ scope.row.status ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="tableColumns.find((col) => col.prop === 'created_id')?.show" label="创建人ID" prop="created_id" min-width="140">
        </el-table-column>
        <el-table-column v-if="tableColumns.find((col) => col.prop === 'updated_id')?.show" label="更新人ID" prop="updated_id" min-width="140">
        </el-table-column>
        <el-table-column v-if="tableColumns.find(col => col.prop === 'operation')?.show" fixed="right" label="操作" align="center" min-width="180">
          <template #default="scope">
            <el-button v-hasPerm="['module_gencode:gen_demo:detail']" type="info" size="small" link icon="document" @click="handleOpenDialog('detail', scope.row.id)">详情</el-button>
            <el-button v-hasPerm="['module_gencode:gen_demo:update']" type="primary" size="small" link icon="edit" @click="handleOpenDialog('update', scope.row.id)">编辑</el-button>
            <el-button v-hasPerm="['module_gencode:gen_demo:delete']" type="danger" size="small" link icon="delete" @click="handleDelete([scope.row.id])">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页区域 -->
      <template #footer>
        <pagination v-model:total="total" v-model:page="queryFormData.page_no" v-model:limit="queryFormData.page_size" @pagination="loadingData" />
      </template>
    </el-card>

    <!-- 弹窗区域 -->
    <el-dialog v-model="dialogVisible.visible" :title="dialogVisible.title" @close="handleCloseDialog">
      <!-- 详情 -->
      <template v-if="dialogVisible.type === 'detail'">
        <el-descriptions :column="4" border>
            <el-descriptions-item label="名称" :span="2">
              {{ detailFormData.name }}
            </el-descriptions-item>
            <el-descriptions-item label="主键ID" :span="2">
              {{ detailFormData.id }}
            </el-descriptions-item>
            <el-descriptions-item label="UUID全局唯一标识" :span="2">
              {{ detailFormData.uuid }}
            </el-descriptions-item>
            <el-descriptions-item label="是否启用(0:启用 1:禁用)" :span="2">
              {{ detailFormData.status }}
            </el-descriptions-item>
            <el-descriptions-item label="备注/描述" :span="2">
              {{ detailFormData.description }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间" :span="2">
              {{ detailFormData.created_time }}
            </el-descriptions-item>
            <el-descriptions-item label="更新时间" :span="2">
              {{ detailFormData.updated_time }}
            </el-descriptions-item>
            <el-descriptions-item label="创建人ID" :span="2">
              {{ detailFormData.created_id }}
            </el-descriptions-item>
            <el-descriptions-item label="更新人ID" :span="2">
              {{ detailFormData.updated_id }}
            </el-descriptions-item>
        </el-descriptions>
      </template>
      <!-- 新增、编辑表单 -->
      <template v-else>
        <el-form ref="dataFormRef" :model="formData" :rules="rules" label-suffix=":" label-width="auto" label-position="right">
          <el-form-item label="名称" prop="name" :required="false">
            <el-input v-model="formData.name" placeholder="请输入名称" />
          </el-form-item>
          <el-form-item label="主键ID" prop="id" :required="false">
            <el-input v-model="formData.id" placeholder="请输入主键ID" />
          </el-form-item>
          <el-form-item label="UUID全局唯一标识" prop="uuid" :required="false">
            <el-input v-model="formData.uuid" placeholder="请输入UUID全局唯一标识" />
          </el-form-item>
          <el-form-item label="状态" prop="status" :required="true">
            <el-radio-group v-model="formData.status">
              <el-radio :value="true">启用</el-radio>
              <el-radio :value="false">停用</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="备注/描述" prop="description" :required="false">
            <el-input v-model="formData.description" placeholder="请输入备注/描述" />
          </el-form-item>
          <el-form-item label="创建时间" prop="created_time" :required="false">
            <el-input v-model="formData.created_time" placeholder="请输入创建时间" />
          </el-form-item>
          <el-form-item label="更新时间" prop="updated_time" :required="false">
            <el-input v-model="formData.updated_time" placeholder="请输入更新时间" />
          </el-form-item>
          <el-form-item label="创建人ID" prop="created_id" :required="false">
            <el-input v-model="formData.created_id" placeholder="请输入创建人ID" />
          </el-form-item>
          <el-form-item label="更新人ID" prop="updated_id" :required="false">
            <el-input v-model="formData.updated_id" placeholder="请输入更新人ID" />
          </el-form-item>
        </el-form>
      </template>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCloseDialog">取消</el-button>
          <el-button v-if="dialogVisible.type !== 'detail'" v-hasPerm="['module_gencode:gen_demo:submit']" type="primary" @click="handleSubmit">确定</el-button>
          <el-button v-else v-hasPerm="['module_gencode:gen_demo:detail']" type="primary" @click="handleCloseDialog">确定</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 导入弹窗 -->
    <ImportModal 
      v-model="importDialogVisible" 
      :content-config="curdContentConfig"
      @upload="handleUpload" 
    />

    <!-- 导出弹窗 -->
    <ExportModal 
      v-model="exportsDialogVisible"
      :content-config="curdContentConfig"
      :query-params="queryFormData"
      :page-data="pageTableData"
      :selection-data="selectionRows"
    />
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "GenDemo",
  inheritAttrs: false,
});
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ResultEnum } from '@/enums/api/result.enum'
import { QuestionFilled, ArrowUp, ArrowDown, Check, CircleClose } from '@element-plus/icons-vue'
import { formatToDateTime } from '@/utils/dateUtil'
import GenDemoAPI, { GenDemoPageQuery, GenDemoTable, GenDemoForm } from '@/api/module_gencode/gen_demo'
import { useDictStore } from '@/store/index'
import SingleImageUpload from '@/components/Upload/SingleImageUpload.vue'
import ImportModal from '@/components/CURD/ImportModal.vue'
import ExportModal from '@/components/CURD/ExportModal.vue'
import DatePicker from '@/components/DatePicker/index.vue'
import type { IContentConfig } from '@/components/CURD/types'

const visible = ref(true)
const isExpand = ref(false)
const isExpandable = ref(true)

const queryFormRef = ref()
const dataFormRef = ref()
const total = ref(0)
const selectIds = ref<number[]>([])
const selectionRows = ref<GenDemoTable[]>([]);
const loading = ref(false)

// 字典仓库与需要加载的字典类型
const dictStore = useDictStore()
const dictTypes = [
]

// 分页表单
const pageTableData = ref<GenDemoTable[]>([]);

// 表格列配置（根据列生成，可显隐）
const tableColumns = ref([
  { prop: 'selection', label: '选择框', show: true },
  { prop: 'index', label: '序号', show: true },
  { prop: 'name', label: '名称', show: true },
  { prop: 'uuid', label: 'UUID全局唯一标识', show: true },
  { prop: 'status', label: '是否启用(0:启用 1:禁用)', show: true },
  { prop: 'created_id', label: '创建人ID', show: true },
  { prop: 'updated_id', label: '更新人ID', show: true },
  { prop: 'operation', label: '操作', show: true }
])

// 导出列（不含选择/序号/操作）
const exportColumns = [
  { prop: 'name', label: '名称' },
  { prop: 'uuid', label: 'UUID全局唯一标识' },
  { prop: 'status', label: '是否启用(0:启用 1:禁用)' },
  { prop: 'created_id', label: '创建人ID' },
  { prop: 'updated_id', label: '更新人ID' },
]

// 导入/导出配置
const curdContentConfig = {
  permPrefix: 'module_gencode:gen_demo',
  cols: exportColumns as any,
  importTemplate: () => GenDemoAPI.downloadTemplateGenDemo(),
  exportsAction: async (params: any) => {
    const query: any = { ...params };
    if (typeof query.status === 'string') {
      query.status = query.status === 'true';
    }
    query.page_no = 1;
    query.page_size = 9999;
    const all: any[] = [];
    while (true) {
      const res = await GenDemoAPI.listGenDemo(query)
      const items = res.data?.data?.items || []
      const total = res.data?.data?.total || 0
      all.push(...items)
      if (all.length >= total || items.length === 0) break
      query.page_no += 1
    }
    return all;
  },
} as unknown as IContentConfig

// 弹窗状态
const dialogVisible = reactive({
  title: '',
  visible: false,
  type: 'create', // 'create' | 'update' | 'detail'
})

// 编辑表单
const formData = reactive<GenDemoForm>({
  id: undefined,
  name: undefined,
  id: undefined,
  uuid: undefined,
  status: undefined,
  description: undefined,
  created_time: undefined,
  updated_time: undefined,
  created_id: undefined,
  updated_id: undefined,
})

// 定义初始表单数据常量
const initialFormData: GenDemoForm = {
  id: undefined,
  name: undefined,
  id: undefined,
  uuid: undefined,
  status: true,
  description: undefined,
  created_time: undefined,
  updated_time: undefined,
  created_id: undefined,
  updated_id: undefined,
}

// 重置表单
async function resetForm() {
  if (dataFormRef.value) {
    dataFormRef.value.resetFields();
    dataFormRef.value.clearValidate();
  }
  // 完全重置 formData 为初始状态
  Object.assign(formData, initialFormData);
}

// 表单验证规则（必填项按 is_nullable 生成）
const rules = reactive({
  name: [
    { required: false, message: '请输入名称', trigger: 'blur' },
  ],
  id: [
    { required: false, message: '请输入主键ID', trigger: 'blur' },
  ],
  uuid: [
    { required: true, message: '请输入UUID全局唯一标识', trigger: 'blur' },
  ],
  status: [
    { required: true, message: '请输入是否启用(0:启用 1:禁用)', trigger: 'blur' },
  ],
  description: [
    { required: false, message: '请输入备注/描述', trigger: 'blur' },
  ],
  created_time: [
    { required: true, message: '请输入创建时间', trigger: 'blur' },
  ],
  updated_time: [
    { required: true, message: '请输入更新时间', trigger: 'blur' },
  ],
  created_id: [
    { required: false, message: '请输入创建人ID', trigger: 'blur' },
  ],
  updated_id: [
    { required: false, message: '请输入更新人ID', trigger: 'blur' },
  ],
})

// 详情表单
const detailFormData = ref<GenDemoTable>({});


// 统一日期范围
const dateRange = ref<[Date, Date] | []>([]);
function handleDateRangeChange(range: [Date, Date]) {
  dateRange.value = range;
  if (range && range.length === 2) {
    queryFormData.start_time = formatToDateTime(range[0]);
    queryFormData.end_time = formatToDateTime(range[1]);
  } else {
    queryFormData.start_time = undefined;
    queryFormData.end_time = undefined;
  }
}

// 查询参数
const queryFormData = reactive<GenDemoPageQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  uuid: undefined,
  status: undefined,
  created_id: undefined,
  updated_id: undefined,
  start_time: undefined,
  end_time: undefined,
  creator: undefined,
})

// 加载表格数据
async function loadingData() {
  loading.value = true;
  try {
    const response = await GenDemoAPI.listGenDemo(queryFormData);
    pageTableData.value = response.data.data.items;
    total.value = response.data.data.total;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
}

// 查询（重置页码后获取数据）
async function handleQuery() {
  queryFormData.page_no = 1;
  loadingData();
}

// 选择创建人后触发查询
function handleConfirm() {
  handleQuery()
}

// 重置查询
async function handleResetQuery() {
  queryFormRef.value.resetFields();
  queryFormData.page_no = 1;
  dateRange.value = [];
  queryFormData.start_time = undefined;
  queryFormData.end_time = undefined;
  loadingData();
}

// 行复选框选中项变化
function handleSelectionChange(selection: any[]) {
  selectIds.value = selection.map((item: any) => item.id)
  selectionRows.value = selection
}

// 关闭弹窗
async function handleCloseDialog() {
  dialogVisible.visible = false;
  resetForm();
}

// 打开弹窗
async function handleOpenDialog(type: 'create' | 'update' | 'detail', id?: number) {
  dialogVisible.type = type
  if (id) {
    const response = await GenDemoAPI.detailGenDemo(id);
    if (type === 'detail') {
      dialogVisible.title = '详情';
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === 'update') {
      dialogVisible.title = '修改';
      Object.assign(formData, response.data.data);
    }
  } else {
    dialogVisible.title = '新增示例';
    formData.id = undefined;
  }
  dialogVisible.visible = true;
}

// 提交表单
async function handleSubmit() {
  dataFormRef.value.validate(async (valid: any) => {
    if (valid) {
      loading.value = true
      try {
        const id = formData.id
        if (id) {
          await GenDemoAPI.updateGenDemo(id, { id, ...formData });
          dialogVisible.visible = false;
          resetForm();
          handleCloseDialog();
          handleResetQuery();
        } else {
          await GenDemoAPI.createGenDemo(formData);
          dialogVisible.visible = false;
          resetForm();
          handleCloseDialog();
          handleResetQuery();
        }
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }
  })
}

// 删除、批量删除
async function handleDelete(ids: number[]) {
  ElMessageBox.confirm('确认删除该项数据?', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      try {
        loading.value = true;
        await GenDemoAPI.deleteGenDemo(ids);
        handleResetQuery()
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    })
    .catch(() => {
      ElMessageBox.close()
    })
}

// 批量启用/停用
async function handleMoreClick(status: strean) {
  if (selectIds.value.length) {
    ElMessageBox.confirm(`确认${status ? '启用' : '停用'}该项数据?`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }).then(async () => {
      try {
        loading.value = true
        await GenDemoAPI.batchAvailableGenDemo({ ids: selectIds.value, status });
        handleResetQuery()
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }).catch(() => {
      ElMessageBox.close()
    })
  }
}

// 导入弹窗显示状态
const importDialogVisible = ref(false)
// 导出弹窗显示状态
const exportsDialogVisible = ref(false)

// 打开导入弹窗
function handleOpenImportDialog() {
  importDialogVisible.value = true
}
// 打开导出弹窗
function handleOpenExportsModal() {
  exportsDialogVisible.value = true
}

// 处理上传
const handleUpload = async (formData: FormData) => {
  try {
    const response = await GenDemoAPI.importGenDemo(formData);
    if (response.data.code === ResultEnum.SUCCESS) {
      ElMessage.success(`${response.data.msg}，${response.data.data}`)
      importDialogVisible.value = false
      await handleQuery()
    }
  } catch (error) {
    console.error(error)
  }
}

// 列表刷新
async function handleRefresh() {
  await loadingData()
}

onMounted(async () => {
  // 预加载字典数据
  if (dictTypes.length > 0) {
    await dictStore.getDict(dictTypes)
  }
  loadingData()
})
</script>

<style lang="scss" scoped></style>
