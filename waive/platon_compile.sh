#!/bin/bash


# 变量参数定义
export GOPATH=${WORK_DIR}    # 重定义GOPATH环境变量
work_dir=${WORK_DIR}    # 代码路径
git_domain=${GIT_DOMAIN}    # GIT域名或IP地址
git_user=${GIT_USER}    # GIT用户
git_pwd=${GIT_PWD}    # GIT密码
project_group=${PROJECT_GROUP}    # 项目所属组织
project_name=${PROJECT_NAME}    # 项目名称
project_branch=${PROJECT_BRANCH}    # 项目分支
build_type=${BUILD_TYPE}    # 构建类型，Debug/Release（Debug暂不支持）
build_action=${BUILD_ACTION}    # 运行动作，All/Compile/Pack
compile_platform=${COMPILE_PLATFORM}    # 所在系统，Windows/Linux/Unix/Mac（Unix/Mac暂不支持）
pack_platform=${PACK_PLATFORM}    # 打包内容，All/Windows/Linux/Unix/Mac（Unix/Mac暂不支持）


# 打印参数信息
function print_prarm() {
	echo "# 开始打印参数"
	echo "GOPATH = ${GOPATH}"
	echo "work_dir = ${work_dir}"
	echo "git_user = ${git_user}"
	echo "git_pwd = ${git_pwd}"
	echo "git_domain = ${git_domain}"
	echo "project_group = ${project_group}"
	echo "project_name = ${project_name}"
	echo "project_branch = ${project_branch}"
	echo "build_type = ${build_type}"
	echo "build_action = ${build_action}"
	echo "compile_platform = ${compile_platform}"
	echo "pack_content = ${pack_content}"
	echo "# 参数打印完成"
}


# 清理本地缓存
function clear_cache() {
	echo "# 开始清理缓存"
	[ ! -n "${work_dir}" ] && echo '参数为空：${work_dir}' && exit 1
	cd ${work_dir} && rm -rf ./src && rm -rf ./bin && rm -rf ./pkg 
	echo "# 缓存清理完成"
}


# 拉取项目代码
function clone_code() {
	echo "# 开始拉取代码"
	[ ! -n "${work_dir}" ] && echo '参数为空：${work_dir}' && exit 1
	[ ! -n "${project_group}" ] && echo '参数为空：${project_group}' && exit 1
	[ ! -n "${project_name}" ] && echo '参数为空：${project_name}' && exit 1
	[ ! -n "${project_branch}" ] && echo '参数为空：${project_branch}' && exit 1
	cd ${work_dir}
	[ ! -d "./src" ] && rm -rf ./src && mkdir ./src
	[ ! -d "./bin" ] && rm -rf ./bin && mkdir ./bin
	[ ! -d "./pkg" ] && rm -rf ./pkg && mkdir ./pkg
	[ ! -d "./src/github.com" ] && rm -rf ./src/github.com && mkdir ./src/github.com
	[ ! -d "./src/github.com/PlatONnetwork" ] && rm -rf ./src/github.com/PlatONnetwork && mkdir ./src/github.com/PlatONnetwork
	cd ${work_dir}/src/github.com/PlatONnetwork && [ ! -d "${project_name}" ] && rm -rf ${project_name}
	git_clone ${project_group} ${project_name} ${project_branch}
	[ $(ls -l |grep "^d"|wc -l) -eq 1 ] && [ ! -d "PlatON_Go" ] && mv $(ls) PlatON_Go
	echo "# 代码拉取完成"
}


# 代码拉取方法
function git_clone() {
	project_group=$1
	project_name=$2
	project_branch=$3
	[ ! -n "${git_user}" ] && echo '参数为空：${git_user}' && exit 1
	[ ! -n "${git_pwd}" ] && echo '参数为空：${git_pwd}' && exit 1
	[ ! -n "${git_domain}" ] && echo '参数为空：${git_domain}' && exit 1
	[ ! -n "${project_group}" ] && echo '参数为空：${project_group}' && exit 1
	[ ! -n "${project_name}" ] && echo '参数为空：${project_name}' && exit 1
	[ ! -n "${project_branch}" ] && echo '参数为空：${project_branch}' && exit 1
	git_url=http://${git_user}:${git_pwd}@${git_domain}/${project_group}/${project_name}.git
	proxychains git clone --recursive ${git_url}  #通过代理网络clone代码
	cd ${project_name}
	remote_branchs=$(git branch -r)
	remote_tags=$(git tag)
	if ([[ "${remote_branchs}" =~ "${project_branch}" ]] || [[ "${remote_tags}" =~ "${project_branch}" ]]); then
		git reset --hard origin/${project_branch} &>/dev/null
		git checkout ${project_branch} &>/dev/null
		git log --pretty=format:"%h    %s    %cn    %ai" -1
		echo -e "\n"
	else
		echo "错误：${project_name} 项目的 ${project_branch} 分支不存在！" && exit 1
	fi
}


# 编译项目代码
function compile_code() {
	echo "# 开始编译代码"
	[ ! -n "${work_dir}" ] && echo '参数为空：${work_dir}' && exit 1
	[ ! -n "${compile_platform}" ] && echo '参数为空：${compile_platform}' && exit 1
	if [ ${compile_platform} == "linux" ]; then
		cd ${work_dir}/src/github.com/PlatONnetwork/PlatON-Go/build && chmod u+x *.sh
		cd ${work_dir}/src/github.com/PlatONnetwork/PlatON-Go && make clean && make all-with-mpc
	elif [ ${compile_platform} == "windows" ]; then
		cd ${work_dir}/src/github.com/PlatONnetwork/PlatON-Go/build && sh ./build_deps.sh && go run ./ci.go install
	fi
	echo "# 代码编译完成"
}


# 打包程序文件 
function pack_production() {
	echo "# 开始打包文件"
	[ ! -n "${work_dir}" ] && echo '参数为空：${work_dir}' && exit 1
	[ ! -n "${build_type}" ] && echo '参数为空：${build_type}' && exit 1
	[ ! -n "${project_branch}" ] && echo '参数为空：${project_branch}' && exit 1
	tar_name=${build_type}_"Platon-go_"[${project_branch}]"_"$(date "+%y%m%d%H%M")
	cd ${work_dir}/src/github.com/PlatONnetwork/PlatON-Go/build/bin
	i=0
	while [ $i -le 10 ]
	do
		i=$[$i + 1]
		if [ ! -e ${tar_name} ]; then
			mkdir ${tar_name}
			mkdir ${tar_name}/linux
			mkdir ${tar_name}/windows
			break
		else
			tar_name="${tar_name}_r"
		fi
	done
	if [ ${pack_platform} == "Linux" ] || [ ${pack_platform} == "All" ]; then
		[ -d ${tar_name}/linux ] && cp platon ctool ethkey ${tar_name}/linux
	fi
	if [ ${pack_platform} == "Windows" ] || [ ${pack_platform} == "All" ]; then
		[ -d ${tar_name}/windows ] && cp platon.exe ctool.exe ethkey.exe ${tar_name}/windows
	fi
	[ -d ${tar_name} ] && [ ! -e ${tar_name}.tar.gz ] && tar -zcf ${tar_name}.tar.gz ${tar_name}
	echo "# 文件打包完成"
}


# 执行构建程序
if [ ${build_action} == "Compile" ] || [ ${build_action} == "All" ]; then
	print_prarm
	clear_cache
	clone_code
	compile_code
fi
if [ ${build_action} == "Pack" ] || [ ${build_action} == "All" ]; then
	pack_production
fi


